'use client';

import { useState } from 'react';
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
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-3 flex items-center justify-center gap-3">
            <Calculator className="h-12 w-12 text-blue-600" />
            AI Geometry Tutor
          </h1>
          <p className="text-gray-600 text-xl">
            Trợ lý AI thông minh giúp bạn học hình học hiệu quả
          </p>
        </div>

        {/* Question Input - Centered */}
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

          {/* Ask Tutor Button - Below and Right Aligned */}
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-2">
            <Calculator className="h-6 w-6 text-blue-600" />
            AI Geometry Tutor
          </h1>
        </div>
      </div>

      {/* Top Row Panels */}
      <div className="flex-none p-4">
        <div className="grid grid-cols-10 gap-4 h-48">
          {/* Question Space - 60% width (6 cols) */}
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

          {/* Hints Space - 20% width (2 cols) */}
          <Card className="col-span-2">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Gợi ý</CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <div className="space-y-2 h-32 overflow-y-auto">
                {hints.length === 0 ? (
                  <p className="text-xs text-gray-500 text-center mt-8">Chưa có gợi ý</p>
                ) : (
                  hints.map((hint, index) => (
                    <div key={index} className="text-xs bg-yellow-50 p-2 rounded">
                      {hint}
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* Facts Space - 20% width (2 cols) */}
          <Card className="col-span-2">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Kiến thức</CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <div className="space-y-2 h-32 overflow-y-auto">
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
        </div>

        {/* Action Toolbar */}
        <div className="mt-4 flex gap-2">
          <Button variant="outline" size="sm" onClick={handleMoreHints}>
            <Lightbulb className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={handleGetFacts}>
            <ListChecks className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm">
            <PlayCircle className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm">
            <CheckCircle className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm">
            <Eye className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Main Body - Chat and Diagram */}
      <div className="flex-1 p-4 pt-0 min-h-0">
        <div className="grid grid-cols-10 gap-4 h-full">
          {/* Chat Pane - 60% width (6 cols) */}
          <Card className="col-span-6 flex flex-col">
            <CardContent className="flex-1 p-4 flex flex-col min-h-0">
              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto space-y-3 mb-4">
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

              {/* Chat Input */}
              <div className="flex gap-2">
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

          {/* Diagram Viewer - 40% width (4 cols) */}
          <Card className="col-span-4 flex flex-col">
            <CardContent className="flex-1 p-4 flex flex-col min-h-0">
              {/* Diagram Canvas */}
              <div className="flex-1 bg-white border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center relative">
                <div className="text-center text-gray-500">
                  <Eye className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Hình minh họa sẽ xuất hiện tại đây</p>
                  <p className="text-xs text-gray-400 mt-1">Canvas JSXGraph tương tác</p>
                </div>
              </div>

              {/* Diagram Controls */}
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
