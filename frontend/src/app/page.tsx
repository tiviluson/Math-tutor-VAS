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
  X,
  Pentagon
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
  const [showImageModal, setShowImageModal] = useState(false);

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
        // Facts will be loaded automatically by useFacts hook
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
        
        // If answer is correct, immediately refresh facts to show new proven results
        if (isCorrect) {
          await facts.refreshFacts(); // Refresh to update proven facts
          chatMessages.addMessage({
            text: "🎯 Kết quả đã được cập nhật vào phần 'Kết quả đã chứng minh'!",
            isUser: false,
          });
        }
        
        if (validationResponse.moved_to_next) {
          chatMessages.addMessage({
            text: "🎉 Chuyển sang câu hỏi tiếp theo!",
            isUser: false,
          });
          // Also refresh facts when moving to next question
          await facts.refreshFacts();
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
        
        // Refresh facts after viewing solution as it might add new proven results
        await facts.refreshFacts();
        chatMessages.addMessage({
          text: "📚 Kết quả đã được cập nhật vào phần 'Kết quả đã chứng minh'!",
          isUser: false,
        });
        
        if (solutionResponse.moved_to_next) {
          chatMessages.addMessage({
            text: "➡️ Đã chuyển sang câu hỏi tiếp theo.",
            isUser: false,
          });
          // Also refresh facts when moving to next question
          await facts.refreshFacts();
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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100 flex flex-col items-center justify-center p-4">
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-5xl font-bold text-gray-900 mb-3 flex items-center justify-center gap-3">
            <div className="relative">
              <Pentagon className="h-12 w-12 text-blue-600 transition-all duration-300 hover:scale-110 hover:rotate-12" />
              <div className="absolute inset-0 h-12 w-12 bg-blue-600/20 rounded-full animate-ping"></div>
            </div>
            <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
              AI Geometry Tutor
            </span>
          </h1>
          <p className="text-gray-600 text-xl">
            Trợ lý AI thông minh giúp bạn học hình học hiệu quả ✨
          </p>
        </div>

        <div className="w-full max-w-4xl">
          <Card className="relative transition-all duration-300 hover:shadow-2xl hover:scale-[1.02] bg-gradient-to-br from-white/90 to-blue-50/50 backdrop-blur-sm border-white/20">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-blue-600" />
                  <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    Nhập bài toán hình học
                  </span>
                </div>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => document.getElementById('file-upload')?.click()}
                  className="flex items-center gap-2 hover:bg-blue-50 border-blue-200 text-blue-700 transition-all duration-200 hover:scale-105"
                >
                  <Upload className="h-4 w-4" />
                  Upload file
                </Button>
              </CardTitle>
              <CardDescription className="text-slate-600">
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
      <div className="bg-gradient-to-r from-white/95 via-white/90 to-white/95 backdrop-blur-md border-b border-white/30 p-4 flex-shrink-0 shadow-lg">
        <div className="text-center">
          <h1 className="text-xl md:text-2xl font-bold flex items-center justify-center gap-2">
            <Pentagon className="h-5 w-5 md:h-6 md:w-6 text-blue-600 transition-all duration-300 hover:scale-110 hover:rotate-12" />
            <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
              AI Geometry Tutor
            </span>
          </h1>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex gap-6 w-full min-h-0 pl-6 pr-6 py-4">
        {/* Left Side - Control Cards */}
        <div className="w-[45%] flex flex-col gap-4">
          {/* Visualization Card */}
          <div className="bg-gradient-to-br from-white/90 to-purple-50/80 backdrop-blur-sm rounded-2xl shadow-lg border border-purple-200/60 p-4 h-[60%] transition-all duration-300 hover:shadow-xl hover:scale-[1.02]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <Eye className="h-5 w-5 text-purple-600" />
                Hình minh họa
              </h3>
              <div className="flex gap-2">
                <Button
                  variant={showVisualizationModal ? "default" : "outline"}
                  size="sm"
                  onClick={() => setShowVisualizationModal(!showVisualizationModal)}
                  className={showVisualizationModal ? 
                    "bg-purple-600 text-white hover:bg-purple-700" : 
                    "border-purple-200 text-purple-700 hover:bg-purple-50"
                  }
                >
                  {showVisualizationModal ? "Ẩn" : "Hiện"}
                </Button>
                {showVisualizationModal && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => visualization.getVisualization()}
                    disabled={visualization.isLoading || !session.sessionId}
                    className="border-purple-200 text-purple-700 hover:bg-purple-50"
                  >
                    {visualization.isLoading ? (
                      <>
                        <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                        Tạo hình
                      </>
                    ) : (
                      <>
                        <RotateCcw className="mr-1 h-4 w-4" />
                        Làm mới
                      </>
                    )}
                  </Button>
                )}
              </div>
            </div>
            
            {/* Visualization Display Area */}
            {showVisualizationModal && (
              <div className="h-[calc(100%-80px)] bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg p-4 flex items-center justify-center border border-slate-200 overflow-hidden">
                {visualization.plotData ? (
                  <img 
                    src={`data:image/jpeg;base64,${visualization.plotData}`}
                    alt="Geometric Visualization"
                    className="max-w-full max-h-full object-contain rounded-lg shadow-md cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-lg"
                    onClick={() => setShowImageModal(true)}
                    title="Click để phóng to"
                  />
                ) : visualization.isLoading ? (
                  <div className="text-center text-blue-600">
                    <Loader2 className="h-12 w-12 mx-auto mb-4 animate-spin" />
                    <p className="text-lg font-medium">Đang tạo hình minh họa...</p>
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
            )}
            
            {/* Download button */}
            {showVisualizationModal && visualization.plotData && (
              <div className="flex justify-center mt-2">
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

          {/* Known Facts Card */}
          <div className="bg-gradient-to-br from-white/90 to-emerald-50/80 backdrop-blur-sm rounded-2xl shadow-lg border border-emerald-200/60 p-4 h-[40%] transition-all duration-300 hover:shadow-xl hover:scale-[1.02]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-emerald-600" />
                Kết quả đã chứng minh
              </h3>
              <div className="flex gap-2">
                {facts.isLoading && (
                  <Loader2 className="h-4 w-4 animate-spin text-emerald-600" />
                )}
                {facts.facts.length > 0 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowKnowledgeModal(true)}
                    className="border-emerald-200 text-emerald-700 hover:bg-emerald-50"
                  >
                    <BookOpen className="mr-1 h-4 w-4" />
                    Xem tất cả
                  </Button>
                )}
              </div>
            </div>
            
            {/* Facts Display Area */}
            <div className="h-[calc(100%-60px)] overflow-y-auto scrollbar-custom">
              {facts.facts.length > 0 ? (
                <div className="space-y-2">
                  {facts.facts.slice(0, 5).map((fact, index) => (
                    <div 
                      key={index} 
                      className="text-sm bg-gradient-to-r from-emerald-50 to-emerald-100 p-3 rounded-lg border-l-4 border-emerald-400 shadow-sm animate-fade-in"
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <div className="flex items-start gap-2">
                        <CheckCircle className="h-4 w-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                        <span className="text-slate-700">{fact}</span>
                      </div>
                    </div>
                  ))}
                  {facts.facts.length > 5 && (
                    <div className="text-center pt-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowKnowledgeModal(true)}
                        className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
                      >
                        +{facts.facts.length - 5} kết quả khác
                      </Button>
                    </div>
                  )}
                </div>
              ) : facts.error ? (
                <div className="text-center text-red-500 h-full flex items-center justify-center">
                  <div>
                    <HelpCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm font-medium">Lỗi khi tải dữ liệu</p>
                    <p className="text-xs text-slate-500 mt-1">{facts.error}</p>
                  </div>
                </div>
              ) : (
                <div className="text-center text-slate-400 h-full flex items-center justify-center">
                  <div>
                    <BookOpen className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm font-medium">Chưa có kết quả nào được chứng minh</p>
                    <p className="text-xs mt-1">Các kết quả sẽ xuất hiện khi bạn giải bài</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Side - Chat Area */}
        <div className="flex-1 flex flex-col min-h-0">
          {/* Chat Messages */}
          <div 
            className="overflow-y-auto p-4 space-y-4 scrollbar-custom flex-1 mb-4"
            style={{ 
              maxHeight: 'calc(100vh - 200px)',
              minHeight: '300px'
            }}
            ref={chatContainerRef}
          >
            {chatMessages.messages.map((message, index) => (
              <div key={index} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
                <div className={`max-w-sm md:max-w-lg lg:max-w-xl xl:max-w-2xl px-4 py-3 transition-all duration-300 hover:scale-105 ${
                  message.isUser 
                    ? 'bg-gradient-to-r from-blue-500 via-blue-600 to-indigo-600 text-white rounded-2xl rounded-br-none shadow-lg hover:shadow-xl' 
                    : 'bg-gradient-to-r from-white to-gray-50 text-slate-800 shadow-md border border-slate-200/60 rounded-2xl rounded-bl-none hover:shadow-lg'
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
                <div className="text-center animate-fade-in">
                  <div className="relative">
                    <Pentagon className="h-16 w-16 mx-auto mb-4 text-blue-400 animate-pulse" />
                    <div className="absolute inset-0 h-16 w-16 mx-auto mb-4 bg-blue-400/20 rounded-full animate-ping"></div>
                  </div>
                  <p className="text-slate-600 text-lg mb-2 font-medium">Chào mừng đến với AI Geometry Tutor!</p>
                  <p className="text-slate-400 text-sm">Hãy bắt đầu cuộc hành trình học tập của bạn ✨</p>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-white/30 bg-white/80 backdrop-blur-xl p-4 flex-shrink-0 shadow-2xl rounded-3xl border border-white/20 transition-all duration-300 hover:bg-white/90">
            {isWaitingForValidation ? (
              // Validation Input
              <div className="flex gap-2 items-center">
                <Input
                  placeholder="Nhập câu trả lời của bạn..."
                  value={validationAnswer}
                  onChange={(e) => setValidationAnswer(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSubmitValidation()}
                  className="flex-1 rounded-full border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white/80 h-11"
                />
                <Button 
                  onClick={handleSubmitValidation} 
                  size="sm" 
                  disabled={!validationAnswer.trim() || validation.isLoading}
                  className="rounded-full p-3 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 h-12 w-12"
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
                  className="rounded-full border-slate-300 hover:bg-slate-50 h-12 w-12"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              // Normal Chat Input with Feature Icons
              <div className="flex gap-2 items-center">
                {/* Feature Icons */}
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowQuestionModal(true)}
                    className="rounded-full hover:bg-blue-50 text-blue-600 hover:text-blue-700 h-12 w-12 transition-all duration-200 hover:scale-110 hover:shadow-lg"
                    title="Câu hỏi"
                  >
                    <HelpCircle className="h-6 w-6" />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleGetHint}
                    disabled={hint.isLoading}
                    className="rounded-full hover:bg-yellow-50 text-yellow-600 hover:text-yellow-700 h-12 w-12 transition-all duration-200 hover:scale-110 hover:shadow-lg"
                    title="Gợi ý"
                  >
                    {hint.isLoading ? (
                      <Loader2 className="h-6 w-6 animate-spin" />
                    ) : (
                      <Lightbulb className="h-6 w-6" />
                    )}
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsWaitingForValidation(true)}
                    disabled={!session.sessionId}
                    className="rounded-full hover:bg-green-50 text-green-600 hover:text-green-700 h-12 w-12 transition-all duration-200 hover:scale-110 hover:shadow-lg"
                    title="Kiểm tra"
                  >
                    <CheckCircle className="h-6 w-6" />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleGetSolution}
                    disabled={solution.isLoading}
                    className="rounded-full hover:bg-orange-50 text-orange-600 hover:text-orange-700 h-12 w-12 transition-all duration-200 hover:scale-110 hover:shadow-lg"
                    title="Lời giải"
                  >
                    {solution.isLoading ? (
                      <Loader2 className="h-6 w-6 animate-spin" />
                    ) : (
                      <FileText className="h-6 w-6" />
                    )}
                  </Button>
                </div>
                
                <Input
                  placeholder="Hỏi tôi bất cứ điều gì..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendChat()}
                  className="flex-1 rounded-full border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white/80 h-11"
                />
                
                <Button 
                  onClick={handleSendChat} 
                  disabled={!chatInput.trim() || chatMessages.isLoading}
                  className="rounded-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 transition-all duration-200 hover:scale-105 shadow-lg h-11 w-11"
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
      </div>
        
      {/* Disclaimer */}
      <div className="px-4 py-1 text-center">
        <p className="text-xs text-slate-400/60">
          Đáp án từ AI Tutor chỉ mang tính tham khảo, hãy kiểm tra lại để chắc chắn.
        </p>
      </div>

      {/* Modals */}
      {/* Simple Image Modal - Full screen image display */}
      {showImageModal && visualization.plotData && (
        <div 
          className="fixed inset-0 bg-black/90 flex items-center justify-center p-4 z-50 cursor-pointer"
          onClick={() => setShowImageModal(false)}
        >
          <img 
            src={`data:image/jpeg;base64,${visualization.plotData}`}
            alt="Geometric Visualization - Full Size"
            className="max-w-full max-h-full object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}

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
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden shadow-2xl">
            <div className="flex justify-between items-center p-4 border-b bg-gradient-to-r from-emerald-50 to-emerald-100">
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-emerald-600" />
                Tất cả kết quả đã chứng minh
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowKnowledgeModal(false)}
                className="hover:bg-emerald-100"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              <div className="space-y-3">
                {facts.facts.length === 0 ? (
                  <div className="text-center py-12">
                    <BookOpen className="h-16 w-16 mx-auto mb-4 text-slate-300" />
                    <p className="text-slate-500 text-lg font-medium">Chưa có kết quả nào được chứng minh</p>
                    <p className="text-slate-400 text-sm mt-2">Các kết quả sẽ xuất hiện khi bạn giải bài</p>
                  </div>
                ) : (
                  facts.facts.map((fact, index) => (
                    <div 
                      key={index} 
                      className="text-sm bg-gradient-to-r from-emerald-50 to-emerald-100 p-4 rounded-lg border-l-4 border-emerald-400 shadow-sm animate-fade-in"
                      style={{ animationDelay: `${index * 0.05}s` }}
                    >
                      <div className="flex items-start gap-2">
                        <CheckCircle className="h-4 w-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                        <span className="text-slate-700 leading-relaxed">{fact}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
            {facts.facts.length > 0 && (
              <div className="p-4 border-t bg-slate-50 text-center">
                <p className="text-xs text-slate-500">
                  Tổng cộng {facts.facts.length} kết quả đã được chứng minh
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
