'use client';

import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Calculator, 
  Upload, 
  MessageCircle, 
  Lightbulb, 
  ListChecks, 
  PlayCircle, 
  CheckCircle, 
  Eye,
  Send,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  BookOpen,
  HelpCircle,
  FileText,
  Loader2,
  ImageIcon,
  X
} from 'lucide-react';

// Import our custom hooks
import { 
  useTutorSession, 
  useChatMessages, 
  useFacts, 
  useHint, 
  useValidation, 
  useSolution, 
  useVisualization,
  useAutoScroll 
} from '@/lib/hooks';
import { ChatMessage } from '@/lib/api';
import { MessageRenderer } from '@/components/MessageRenderer';

type AppMode = 'ask' | 'workspace';

export default function Home() {
  const [mode, setMode] = useState<AppMode>('ask');
  const [question, setQuestion] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [validationAnswer, setValidationAnswer] = useState('');
  const [isWaitingForValidation, setIsWaitingForValidation] = useState(false);
  
  // Modal states for the messenger-style UI
  const [showQuestionModal, setShowQuestionModal] = useState(false);
  const [showKnowledgeModal, setShowKnowledgeModal] = useState(false);
  const [showVisualizationModal, setShowVisualizationModal] = useState(false);

  // Initialize hooks
  const session = useTutorSession();
  const chatMessages = useChatMessages(session.sessionId);
  const facts = useFacts(session.sessionId);
  const hint = useHint(session.sessionId);
  const validation = useValidation(session.sessionId);
  const solution = useSolution(session.sessionId);
  const visualization = useVisualization(session.sessionId);
  
  // Auto-scroll chat container
  const chatContainerRef = useAutoScroll(chatMessages.messages);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      if (file.type.startsWith('text/') || file.name.endsWith('.txt')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target?.result as string;
          setQuestion(content);
        };
        reader.readAsText(file);
      }
    }
  };

  const handleAskTutor = async () => {
    if (!question.trim()) return;
    
    try {
      const response = await session.createSession(question);
      if (response.success) {
        setMode('workspace');
        chatMessages.addInitialMessage(question);
        // Load initial facts
        await facts.getFacts();
      }
    } catch (error) {
      console.error('Failed to create session:', error);
      // Show error message
      alert('Không thể tạo phiên học tập. Vui lòng thử lại.');
    }
  };

  const handleSendChat = async () => {
    if (!chatInput.trim()) return;
    const messageText = chatInput;
    setChatInput('');
    await chatMessages.sendMessage(messageText);
  };

  const handleGetHint = async () => {
    if (!session.sessionId) return;
    
    try {
      const hintResponse = await hint.getHint();
      if (hintResponse?.success) {
        chatMessages.addMessage({
          text: `💡 Gợi ý: ${hintResponse.hint_text}`,
          isUser: false,
        });
        
        if (hintResponse.max_hints_reached) {
          chatMessages.addMessage({
            text: "⚠️ Bạn đã sử dụng hết số lượng gợi ý cho câu hỏi này.",
            isUser: false,
          });
        }
      } else {
        chatMessages.addMessage({
          text: "❌ Không thể lấy gợi ý lúc này. Vui lòng thử lại.",
          isUser: false,
        });
      }
    } catch (error) {
      console.error('Error getting hint:', error);
      chatMessages.addMessage({
        text: "❌ Có lỗi xảy ra khi lấy gợi ý. Vui lòng thử lại.",
        isUser: false,
      });
    }
  };

  const handleValidate = () => {
    if (!session.sessionId) return;
    
    setIsWaitingForValidation(true);
    chatMessages.addMessage({
      text: "📝 Vui lòng nhập câu trả lời của bạn để tôi kiểm tra:",
      isUser: false,
    });
  };

  const handleSubmitValidation = async () => {
    if (!validationAnswer.trim() || !session.sessionId) return;
    
    const answer = validationAnswer;
    setValidationAnswer('');
    setIsWaitingForValidation(false);
    
    // Add user's answer to chat
    chatMessages.addMessage({
      text: answer,
      isUser: true,
    });
    
    try {
      const validationResponse = await validation.validateSolution(answer);
      if (validationResponse?.success) {
        const isCorrect = validationResponse.is_correct;
        chatMessages.addMessage({
          text: `${isCorrect ? '✅' : '❌'} ${validationResponse.feedback}`,
          isUser: false,
        });
        
        if (validationResponse.moved_to_next) {
          chatMessages.addMessage({
            text: "🎉 Chuyển sang câu hỏi tiếp theo!",
            isUser: false,
          });
        }
      } else {
        chatMessages.addMessage({
          text: "❌ Không thể kiểm tra câu trả lời lúc này. Vui lòng thử lại.",
          isUser: false,
        });
      }
    } catch (error) {
      console.error('Error validating solution:', error);
      chatMessages.addMessage({
        text: "❌ Có lỗi xảy ra khi kiểm tra câu trả lời. Vui lòng thử lại.",
        isUser: false,
      });
    }
  };

  const handleGetSolution = async () => {
    if (!session.sessionId) return;
    
    try {
      const solutionResponse = await solution.getSolution();
      if (solutionResponse?.success) {
        chatMessages.addMessage({
          text: `📖 Lời giải: ${solutionResponse.solution_text}`,
          isUser: false,
        });
        
        if (solutionResponse.moved_to_next) {
          chatMessages.addMessage({
            text: "➡️ Đã chuyển sang câu hỏi tiếp theo.",
            isUser: false,
          });
        }
      } else {
        chatMessages.addMessage({
          text: "❌ Không thể lấy lời giải lúc này. Vui lòng thử lại.",
          isUser: false,
        });
      }
    } catch (error) {
      console.error('Error getting solution:', error);
      chatMessages.addMessage({
        text: "❌ Có lỗi xảy ra khi lấy lời giải. Vui lòng thử lại.",
        isUser: false,
      });
    }
  };

  if (mode === 'ask') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col items-center justify-center p-4">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-3 flex items-center justify-center gap-3">
            <Calculator className="h-12 w-12 text-blue-600" />
            AI Geometry Tutor
          </h1>
          <p className="text-gray-600 text-xl">
            Trợ lý AI thông minh giúp bạn học hình học hiệu quả
          </p>
        </div>

        <div className="w-full max-w-4xl">
          <Card className="relative">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5" />
                  Nhập bài toán hình học
                </div>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => document.getElementById('file-upload')?.click()}
                  className="flex items-center gap-2"
                >
                  <Upload className="h-4 w-4" />
                  Upload file
                </Button>
              </CardTitle>
              <CardDescription>
                Mô tả chi tiết bài toán bạn cần giải quyết hoặc upload file đề bài
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <input
                id="file-upload"
                type="file"
                accept=".txt,.pdf,.doc,.docx,image/*"
                onChange={handleFileUpload}
                className="hidden"
              />
              <Textarea
                placeholder="Ví dụ: Cho tam giác ABC vuông tại A, AB = 3cm, AC = 4cm. Tính chu vi và diện tích tam giác ABC..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="min-h-32"
              />
              {uploadedFile && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Upload className="h-4 w-4" />
                  <span>Đã upload: {uploadedFile.name}</span>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="flex justify-end mt-4">
            <Button 
              onClick={handleAskTutor}
              disabled={!question.trim() || session.isLoading}
              size="lg"
              className="px-8 py-3 text-lg flex items-center gap-3"
            >
              {session.isLoading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Đang xử lý...
                </>
              ) : (
                <>
                  <MessageCircle className="h-5 w-5" />
                  Hỏi Tutor
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-white/90 backdrop-blur-md border-b border-slate-200/60 p-4 flex-shrink-0 shadow-sm">
        <div className="text-center">
          <h1 className="text-xl md:text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent flex items-center justify-center gap-2">
            <Calculator className="h-5 w-5 md:h-6 md:w-6 text-blue-600" />
            AI Geometry Tutor
          </h1>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full min-h-0">
        {/* Chat Messages */}
        <div 
          className="overflow-y-auto p-4 space-y-4 scrollbar-custom"
          style={{ 
            height: 'calc(100vh - 220px)',
            maxHeight: 'calc(100vh - 220px)',
            minHeight: '300px'
          }}
          ref={chatContainerRef}
        >
          {chatMessages.messages.map((message, index) => (
            <div key={index} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-sm md:max-w-lg lg:max-w-xl xl:max-w-2xl px-4 py-3 ${
                message.isUser 
                  ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl rounded-br-none shadow-lg' 
                  : 'bg-white text-slate-800 shadow-md border border-slate-200/60 rounded-2xl rounded-bl-none'
              }`}>
                <MessageRenderer 
                  content={message.text} 
                  isUser={message.isUser} 
                />
              </div>
            </div>
          ))}
          
          {chatMessages.messages.length === 0 && (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <Calculator className="h-16 w-16 mx-auto mb-4 text-slate-300" />
                <p className="text-slate-600 text-lg mb-2">Chào mừng đến với AI Geometry Tutor!</p>
                <p className="text-slate-400 text-sm">Hãy bắt đầu cuộc hành trình học tập của bạn</p>
              </div>
            </div>
          )}
        </div>

        {/* Feature Buttons Row */}
        <div className="flex flex-row justify-center gap-2 flex-wrap px-4 pb-4">
          <Button
            variant="outline"
            size="default"
            onClick={() => setShowQuestionModal(true)}
            className="bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100 hover:border-blue-300"
          >
            Câu hỏi
          </Button>
          
          <Button
            variant="outline"
            size="default"
            onClick={() => setShowKnowledgeModal(true)}
            className="bg-emerald-50 border-emerald-200 text-emerald-700 hover:bg-emerald-100 hover:border-emerald-300"
          >
            Kiến thức liên quan
          </Button>
          
          <Button
            variant="outline"
            size="default"
            onClick={() => setShowVisualizationModal(true)}
            className="bg-purple-50 border-purple-200 text-purple-700 hover:bg-purple-100 hover:border-purple-300"
          >
            Hình minh họa
          </Button>
          
          <Button
            variant="outline"
            size="default"
            onClick={handleGetHint}
            disabled={hint.isLoading}
            className="bg-yellow-50 border-yellow-200 text-yellow-700 hover:bg-yellow-100 hover:border-yellow-300"
          >
            {hint.isLoading ? (
              <>
                <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                Gợi ý
              </>
            ) : (
              'Gợi ý'
            )}
          </Button>
          
          <Button
            variant="outline"
            size="default"
            onClick={() => setIsWaitingForValidation(true)}
            disabled={!session.sessionId}
            className="bg-green-50 border-green-200 text-green-700 hover:bg-green-100 hover:border-green-300"
          >
            Kiểm tra
          </Button>
          
          <Button
            variant="outline"
            size="default"
            onClick={handleGetSolution}
            disabled={solution.isLoading}
            className="bg-orange-50 border-orange-200 text-orange-700 hover:bg-orange-100 hover:border-orange-300"
          >
            {solution.isLoading ? (
              <>
                <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                Lời giải
              </>
            ) : (
              'Lời giải'
            )}
          </Button>
        </div>

        {/* Input Area */}
        <div className="border-t border-slate-200/60 bg-white/70 backdrop-blur-md p-6 flex-shrink-0 shadow-lg">
          {isWaitingForValidation ? (
            // Validation Input
            <div className="flex gap-2 items-center">
              <Input
                placeholder="Nhập câu trả lời của bạn..."
                value={validationAnswer}
                onChange={(e) => setValidationAnswer(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSubmitValidation()}
                className="flex-1 border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
              <Button 
                onClick={handleSubmitValidation} 
                size="sm" 
                disabled={!validationAnswer.trim() || validation.isLoading}
                className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
              >
                {validation.isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <CheckCircle className="h-4 w-4" />
                )}
              </Button>
              <Button 
                onClick={() => setIsWaitingForValidation(false)} 
                variant="outline"
                size="sm"
                className="border-slate-300 hover:bg-slate-50"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            // Normal Chat Input
            <div className="flex gap-2 items-center">
              <Input
                placeholder="Hỏi tôi bất cứ điều gì..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendChat()}
                className="flex-1 rounded-full border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white/80"
              />
              
              <Button 
                onClick={handleSendChat} 
                disabled={!chatInput.trim() || chatMessages.isLoading}
                className="rounded-full p-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 transition-all duration-200 hover:scale-105 shadow-lg"
                size="sm"
              >
                {chatMessages.isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      {/* Question Modal */}
      {showQuestionModal && (
        <div className="fixed inset-0 bg-white/20 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-semibold">Câu hỏi</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowQuestionModal(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="p-4 overflow-y-auto">
              <div className="text-sm bg-slate-50 rounded-lg p-4 leading-relaxed border border-slate-200">
                {question || "Chưa có câu hỏi nào được tải."}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Knowledge Modal */}
      {showKnowledgeModal && (
        <div className="fixed inset-0 bg-white/20 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-semibold">Kiến thức</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowKnowledgeModal(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="p-4 overflow-y-auto">
              <div className="space-y-3">
                {facts.facts.length === 0 ? (
                  <p className="text-slate-500 text-center py-8">Chưa có kiến thức nào</p>
                ) : (
                  facts.facts.map((fact, index) => (
                    <div key={index} className="text-sm bg-emerald-50 p-3 rounded-lg border-l-4 border-emerald-400 shadow-sm">
                      {fact}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Visualization Modal */}
      {showVisualizationModal && (
        <div className="fixed inset-0 bg-white/20 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-semibold">Hình minh họa</h3>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => visualization.getVisualization()}
                  disabled={visualization.isLoading || !session.sessionId}
                >
                  {visualization.isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <RotateCcw className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowVisualizationModal(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="p-4 overflow-y-auto flex-1">
              <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg p-4 min-h-[400px] flex items-center justify-center border border-slate-200">
                {visualization.plotData ? (
                  <img 
                    src={`data:image/jpeg;base64,${visualization.plotData}`}
                    alt="Geometric Visualization"
                    className="max-w-full max-h-full object-contain rounded-lg shadow-md"
                  />
                ) : visualization.isLoading ? (
                  <div className="text-center text-blue-600">
                    <Loader2 className="h-12 w-12 mx-auto mb-4 animate-spin" />
                    <p className="text-lg font-medium">Đang tạo hình minh họa...</p>
                    <p className="text-sm text-slate-500 mt-2">Asymptote đang render</p>
                  </div>
                ) : visualization.error ? (
                  <div className="text-center text-red-500">
                    <HelpCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p className="text-lg font-medium">Không thể tạo hình minh họa</p>
                    <p className="text-sm text-slate-500 mt-2">{visualization.error}</p>
                  </div>
                ) : (
                  <div className="text-center text-slate-500">
                    <ImageIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p className="text-lg font-medium">Hình minh họa sẽ xuất hiện tại đây</p>
                    <p className="text-sm text-slate-400 mt-2">Nhấn nút tải lại để tạo minh họa</p>
                  </div>
                )}
              </div>
              {visualization.plotData && (
                <div className="flex justify-center mt-4">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => {
                      const link = document.createElement('a');
                      link.href = `data:image/jpeg;base64,${visualization.plotData}`;
                      link.download = 'geometry-illustration.jpg';
                      link.click();
                    }}
                    className="flex items-center gap-2"
                  >
                    <FileText className="h-4 w-4" />
                    Tải xuống
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
