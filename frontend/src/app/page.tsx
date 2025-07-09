'use client';

import { useState } from 'react';
import Image from 'next/image';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Calculator, 
  Upload, 
  MessageCircle, 
  ListChecks, 
  Eye,
  Send,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  BookOpen
} from 'lucide-react';
import { 
  useTutorSession, 
  useChatMessages, 
  useFacts, 
  useVisualization,
  useAutoScroll 
} from '@/lib/hooks';
import { 
  LoadingSpinner, 
  ErrorDisplay, 
  LoadingOverlay, 
  ChatLoading, 
  EmptyState 
} from '@/components/ui/loading';

type AppMode = 'ask' | 'workspace';

export default function Home() {
  const [mode, setMode] = useState<AppMode>('ask');
  const [question, setQuestion] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  // Custom hooks for API integration
  const { 
    sessionId, 
    isLoading: sessionLoading, 
    error: sessionError, 
    createSession, 
    clearError: clearSessionError 
  } = useTutorSession();

  const { 
    messages, 
    isLoading: chatLoading, 
    error: chatError, 
    sendMessage, 
    addInitialMessage, 
    clearError: clearChatError 
  } = useChatMessages(sessionId);

  const { 
    facts, 
    isLoading: factsLoading, 
    error: factsError, 
    getFacts,
    clearError: clearFactsError 
  } = useFacts(sessionId);

  const { 
    plotData, 
    plotDescription, 
    isLoading: visualLoading, 
    error: visualError, 
    getVisualization,
    clearError: clearVisualError 
  } = useVisualization(sessionId);

  const chatContainerRef = useAutoScroll(messages);

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
      const response = await createSession(question);
      if (response.success) {
        setMode('workspace');
        addInitialMessage(question);
      }
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const handleSendChat = async () => {
    if (!chatInput.trim()) return;
    
    const messageText = chatInput;
    setChatInput('');
    await sendMessage(messageText);
  };

  const handleGetFacts = async () => {
    await getFacts();
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
              disabled={!question.trim() || sessionLoading}
              size="lg"
              className="px-8 py-3 text-lg flex items-center gap-3"
            >
              {sessionLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <MessageCircle className="h-5 w-5" />
              )}
              {sessionLoading ? 'Đang phân tích...' : 'Hỏi Tutor'}
            </Button>
          </div>

          {sessionError && (
            <div className="mt-4">
              <ErrorDisplay 
                error={sessionError} 
                onRetry={clearSessionError} 
              />
            </div>
          )}
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

      <div className="flex-1 p-4 overflow-hidden">
        <div className="grid grid-cols-10 gap-4 h-full">
          <div className="col-span-6 flex flex-col">
            <Card className="flex-shrink-0 mb-4">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Câu hỏi</CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <div className="text-sm bg-gray-50 rounded p-3 h-12 overflow-y-auto mb-4">
                  {question}
                </div>
                <div className="flex justify-center">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleGetFacts}
                    disabled={factsLoading || !sessionId}
                  >
                    {factsLoading ? (
                      <LoadingSpinner size="sm" className="mr-2" />
                    ) : (
                      <ListChecks className="h-4 w-4 mr-2" />
                    )}
                    Get facts
                  </Button>
                </div>
                {factsError && (
                  <div className="mt-2">
                    <ErrorDisplay 
                      error={factsError} 
                      onRetry={clearFactsError} 
                    />
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="h-[66vh] flex flex-col">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Trò chuyện với AI Tutor</CardTitle>
              </CardHeader>
              <CardContent className="h-full p-4 pt-0 flex flex-col">
                {/* Chat container với chiều cao linh hoạt */}
                <div className="flex-1 overflow-y-auto space-y-3 mb-1 pr-2 border border-gray-200 rounded-lg p-3 bg-gray-50 scrollbar-custom" ref={chatContainerRef}>
                  {messages.map((message, index) => (
                    <div key={index} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs rounded-lg p-3 text-sm ${
                        message.isUser 
                          ? 'bg-blue-500 text-white' 
                          : 'bg-white text-gray-900 shadow-sm border'
                      }`}>
                        {message.text}
                      </div>
                    </div>
                  ))}
                  {chatLoading && <ChatLoading />}
                  {messages.length === 0 && !sessionLoading && (
                    <div className="flex items-center justify-center h-full">
                      <p className="text-gray-400 text-sm">Hãy bắt đầu cuộc hành trình học tập của bạn</p>
                    </div>
                  )}
                </div>

                {chatError && (
                  <div className="my-1">
                    <ErrorDisplay 
                      error={chatError} 
                      onRetry={clearChatError} 
                    />
                  </div>
                )}

                <div className="flex gap-2 flex-shrink-0 mt-4">
                  <Input
                    placeholder="Hỏi tôi bất cứ điều gì..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !chatLoading && handleSendChat()}
                    disabled={chatLoading || !sessionId}
                    className="flex-1"
                  />
                  <Button 
                    onClick={handleSendChat} 
                    size="sm"
                    disabled={chatLoading || !sessionId || !chatInput.trim()}
                  >
                    {chatLoading ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="col-span-4 flex flex-col h-full gap-4">
            <Card className="h-1/3">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Kiến thức</CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0 flex-1">
                <LoadingOverlay isLoading={factsLoading} message="Đang phân tích kiến thức...">
                  <div className="space-y-2 h-full overflow-y-auto">
                    {facts.length === 0 ? (
                      <EmptyState
                        title="Chưa có kiến thức"
                        description="Nhấn 'Get facts' để phân tích bài toán"
                        className="mt-8"
                      />
                    ) : (
                      facts.map((fact, index) => (
                        <div key={index} className="text-xs bg-blue-50 p-2 rounded">
                          {fact}
                        </div>
                      ))
                    )}
                  </div>
                </LoadingOverlay>
                {factsError && (
                  <div className="mt-2">
                    <ErrorDisplay 
                      error={factsError} 
                      onRetry={clearFactsError} 
                    />
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="h-2/3">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Hình minh họa</CardTitle>
              </CardHeader>
              <CardContent className="flex-1 p-4 pt-0 flex flex-col">
                <LoadingOverlay isLoading={visualLoading} message="Đang tạo hình minh họa...">
                  <div className="flex-1 bg-white border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center relative">
                    {plotData ? (
                      <div className="flex flex-col items-center w-full h-full">
                        <Image 
                          src={`data:image/png;base64,${plotData}`} 
                          alt={plotDescription || "Geometric visualization"}
                          width={400}
                          height={300}
                          className="max-w-full max-h-full object-contain"
                        />
                        {plotDescription && (
                          <p className="text-xs text-gray-600 mt-2 text-center px-2">
                            {plotDescription}
                          </p>
                        )}
                      </div>
                    ) : (
                      <EmptyState
                        icon={<Eye className="h-12 w-12" />}
                        title="Hình minh họa sẽ xuất hiện tại đây"
                        description="Canvas JSXGraph tương tác"
                      />
                    )}
                  </div>
                </LoadingOverlay>

                {visualError && (
                  <div className="mt-2">
                    <ErrorDisplay 
                      error={visualError} 
                      onRetry={clearVisualError} 
                    />
                  </div>
                )}

                <div className="flex justify-center gap-2 mt-4">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={getVisualization}
                    disabled={visualLoading || !sessionId}
                  >
                    {visualLoading ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                  <Button variant="outline" size="sm" disabled={!plotData}>
                    <ZoomIn className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="sm" disabled={!plotData}>
                    <ZoomOut className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="sm" disabled={!plotData}>
                    <RotateCcw className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
