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
  BookOpen
} from 'lucide-react';

type AppMode = 'ask' | 'workspace';

export default function Home() {
  const [mode, setMode] = useState<AppMode>('ask');
  const [question, setQuestion] = useState('');
  const [chatMessages, setChatMessages] = useState<Array<{text: string, isUser: boolean}>>([]);
  const [chatInput, setChatInput] = useState('');
  const [hints, setHints] = useState<string[]>([]);
  const [facts, setFacts] = useState<string[]>([]);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatMessages]);

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

  const handleAskTutor = () => {
    if (!question.trim()) return;
    setMode('workspace');
    setChatMessages([
      { text: question, isUser: true },
      { text: "Tôi sẽ giúp bạn giải quyết bài toán này từng bước một. Hãy để tôi phân tích câu hỏi của bạn...", isUser: false }
    ]);
  };

  const handleSendChat = () => {
    if (!chatInput.trim()) return;
    setChatMessages(prev => [...prev, 
      { text: chatInput, isUser: true },
      { text: "Để tôi suy nghĩ về vấn đề đó...", isUser: false }
    ]);
    setChatInput('');
  };

  const handleMoreHints = () => {
    setHints(prev => [...prev, `Gợi ý ${prev.length + 1}: Hãy xem xét các tính chất hình học liên quan.`]);
  };

  const handleGetFacts = () => {
    setFacts(prev => [...prev, `Kiến thức ${prev.length + 1}: Mối quan hệ toán học quan trọng đã được xác định.`]);
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
              disabled={!question.trim()}
              size="lg"
              className="px-8 py-3 text-lg flex items-center gap-3"
            >
              <MessageCircle className="h-5 w-5" />
              Hỏi Tutor
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

      <div className="flex-1 p-4 overflow-hidden">
        <div className="grid grid-cols-10 gap-4 h-full">
          <div className="col-span-6 flex flex-col h-full">
            <Card className="flex-shrink-0 mb-4">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Câu hỏi</CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <div className="text-sm bg-gray-50 rounded p-3 h-20 overflow-y-auto mb-4">
                  {question}
                </div>
                <div className="flex justify-between gap-4 flex-wrap">
                  <Button variant="outline" size="sm" onClick={handleGetFacts} className="mb-2 flex-1 mx-1">
                    <ListChecks className="h-4 w-4 mr-2" />
                    Get facts
                  </Button>
                  <Button variant="outline" size="sm" className="mb-2 flex-1 mx-1">
                    <PlayCircle className="h-4 w-4 mr-2" />
                    Get steps
                  </Button>
                  <Button variant="outline" size="sm" className="mb-2 flex-1 mx-1">
                    <Eye className="h-4 w-4 mr-2" />
                    Visualize
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="flex-1 flex flex-col">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Trò chuyện với AI Tutor</CardTitle>
              </CardHeader>
              <CardContent className="h-full p-4 pt-0 flex flex-col">
                <div className="flex-1 overflow-y-auto space-y-3 mb-4 pr-2" ref={chatContainerRef}>
                  {chatMessages.map((message, index) => (
                    <div key={index} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs rounded-lg p-3 text-sm ${
                        message.isUser 
                          ? 'bg-blue-500 text-white' 
                          : 'bg-gray-100 text-gray-900'
                      }`}>
                        {message.text}
                      </div>
                    </div>
                  ))}
                  {chatMessages.length === 0 && (
                    <div className="flex items-center justify-center h-full">
                      <p className="text-gray-400 text-sm">Hãy bắt đầu cuộc hành trình học tập của bạn</p>
                    </div>
                  )}
                </div>

                <div className="flex gap-2 flex-shrink-0">
                  <Input
                    placeholder="Hỏi tôi bất cứ điều gì..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendChat()}
                    className="flex-1"
                  />
                  <Button onClick={handleSendChat} size="sm">
                    <Send className="h-4 w-4" />
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
                <div className="space-y-2 h-full overflow-y-auto">
                  {facts.length === 0 ? (
                    <p className="text-xs text-gray-500 text-center mt-8">Chưa có kiến thức</p>
                  ) : (
                    facts.map((fact, index) => (
                      <div key={index} className="text-xs bg-blue-50 p-2 rounded">
                        {fact}
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="h-2/3">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Hình minh họa</CardTitle>
              </CardHeader>
              <CardContent className="flex-1 p-4 pt-0 flex flex-col">
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
    </div>
  );
}
