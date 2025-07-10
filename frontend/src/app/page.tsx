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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
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
  MoreVertical,
  HelpCircle,
  FileText,
  Loader2
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
    <div className="h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col overflow-hidden">
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 p-4 flex-shrink-0">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-2">
            <Calculator className="h-6 w-6 text-blue-600" />
            AI Geometry Tutor
          </h1>
        </div>
      </div>

      <div className="flex-shrink-0 p-4">
        <div className="grid grid-cols-10 gap-4 h-auto mb-1.5">
          <Card className="col-span-6">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Câu hỏi</CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <div className="text-sm bg-gray-50 rounded p-3 h-32 overflow-y-auto">
                {question}
              </div>
            </CardContent>
          </Card>

          <Card className="col-span-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Kiến thức</CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <div className="space-y-2 h-32 overflow-y-auto">
                {facts.facts.length === 0 ? (
                  <p className="text-xs text-gray-500 text-center mt-8">Chưa có kiến thức</p>
                ) : (
                  facts.facts.map((fact, index) => (
                    <div key={index} className="text-xs bg-blue-50 p-2 rounded">
                      {fact}
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="flex-1 p-4 pt-0 overflow-hidden">
        <div className="grid grid-cols-10 gap-4 h-full">
          <Card className="col-span-6 flex flex-col h-full">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center justify-between">
                <span>Trò chuyện với AI Tutor</span>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuItem onClick={handleGetHint} disabled={hint.isLoading}>
                      {hint.isLoading ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <Lightbulb className="mr-2 h-4 w-4" />
                      )}
                      <span>Xin hint</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={handleValidate} disabled={validation.isLoading}>
                      {validation.isLoading ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <CheckCircle className="mr-2 h-4 w-4" />
                      )}
                      <span>Validate</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={handleGetSolution} disabled={solution.isLoading}>
                      {solution.isLoading ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <FileText className="mr-2 h-4 w-4" />
                      )}
                      <span>Solution</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </CardTitle>
            </CardHeader>
            <CardContent className="h-full p-4 pt-0 flex flex-col">
              <div className="overflow-y-auto space-y-3 mb-4 pr-2" style={{height: '350px'}} ref={chatContainerRef}>
                {chatMessages.messages.map((message, index) => (
                  <div key={index} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-md rounded-lg p-3 ${
                      message.isUser 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <MessageRenderer 
                        content={message.text} 
                        isUser={message.isUser} 
                      />
                    </div>
                  </div>
                ))}
                {chatMessages.messages.length === 0 && (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-gray-400 text-sm">Hãy bắt đầu cuộc hành trình học tập của bạn</p>
                  </div>
                )}
              </div>

              <div className="flex gap-2 flex-shrink-0">
                {isWaitingForValidation ? (
                  <>
                    <Input
                      placeholder="Nhập câu trả lời của bạn..."
                      value={validationAnswer}
                      onChange={(e) => setValidationAnswer(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSubmitValidation()}
                      className="flex-1"
                    />
                    <Button 
                      onClick={handleSubmitValidation} 
                      size="sm" 
                      disabled={!validationAnswer.trim() || validation.isLoading}
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
                    >
                      Hủy
                    </Button>
                  </>
                ) : (
                  <>
                    <Input
                      placeholder="Hỏi tôi bất cứ điều gì..."
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendChat()}
                      className="flex-1"
                    />
                    <Button 
                      onClick={handleSendChat} 
                      size="sm" 
                      disabled={!chatInput.trim() || chatMessages.isLoading}
                    >
                      {chatMessages.isLoading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Send className="h-4 w-4" />
                      )}
                    </Button>
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="col-span-4 flex flex-col h-full">
            <CardContent className="flex-1 p-4 flex flex-col overflow-hidden">
              <div className="flex-1 bg-white border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center relative">
                <div className="text-center text-gray-500">
                  <Eye className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Hình minh họa sẽ xuất hiện tại đây</p>
                  <p className="text-xs text-gray-400 mt-1">Canvas JSXGraph tương tác</p>
                </div>
              </div>

              <div className="flex justify-center gap-2 mt-4">
                <Button variant="outline" size="sm">
                  <ZoomIn className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm">
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm">
                  <RotateCcw className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
