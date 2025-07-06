'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Calculator, Lightbulb, CheckCircle, XCircle, Brain, BookOpen, Upload } from 'lucide-react';

export default function Home() {
  const [problem, setProblem] = useState('');
  const [solution, setSolution] = useState('');
  const [hints, setHints] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [feedback, setFeedback] = useState<{type: 'success' | 'error', message: string} | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      
      if (file.type.startsWith('text/') || file.name.endsWith('.txt')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target?.result as string;
          setProblem(content);
        };
        reader.readAsText(file);
      } else {
        setProblem(`Đã upload file: ${file.name}`);
      }
    }
  };

  const handleSubmitProblem = async () => {
    if (!problem.trim()) return;
    
    setIsLoading(true);
    setProgress(25);

    setTimeout(() => {
      setHints([
        "Hãy xác định các yếu tố đã cho trong bài toán",
        "Vẽ hình minh họa để hiểu rõ hơn về vấn đề",
        "Xác định công thức hoặc định lý liên quan"
      ]);
      setProgress(100);
      setIsLoading(false);
    }, 2000);
  };

  const handleSubmitSolution = async () => {
    if (!solution.trim()) return;
    
    setIsLoading(true);
    setProgress(50);
    
    setTimeout(() => {
      setFeedback({
        type: Math.random() > 0.5 ? 'success' : 'error',
        message: Math.random() > 0.5 
          ? 'Tuyệt vời! Lời giải của bạn đúng và logic rõ ràng.'
          : 'Lời giải chưa chính xác. Hãy kiểm tra lại các bước tính toán.'
      });
      setProgress(100);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center justify-center gap-2">
            <Calculator className="h-8 w-8 text-blue-600" />
            AI Geometry Tutor
          </h1>
          <p className="text-gray-600 text-lg">
            Trợ lý AI thông minh giúp bạn học hình học hiệu quả
          </p>
        </div>

        <Card className="mb-6">
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
              value={problem}
              onChange={(e) => setProblem(e.target.value)}
              className="min-h-32"
            />
            {uploadedFile && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Upload className="h-4 w-4" />
                <span>Đã upload: {uploadedFile.name}</span>
              </div>
            )}
            <div className="flex gap-3 flex-wrap">
              <Button 
                onClick={() => {
                  if (!problem.trim()) return;
                  setIsLoading(true);
                  setProgress(25);
                  setTimeout(() => {
                    setHints([
                      "Hãy xác định các yếu tố đã cho trong bài toán",
                      "Vẽ hình minh họa để hiểu rõ hơn về vấn đề",
                      "Xác định công thức hoặc định lý liên quan"
                    ]);
                    setProgress(100);
                    setIsLoading(false);
                  }, 2000);
                }}
                disabled={!problem.trim() || isLoading}
                className="flex-1"
              >
                {isLoading ? 'Đang tạo gợi ý...' : 'Hint'}
              </Button>
              
              <Button 
                onClick={() => {
                  if (!problem.trim()) return;
                  setIsLoading(true);
                  setProgress(25);
                  setTimeout(() => {
                    setProgress(100);
                    setIsLoading(false);
                  }, 2000);
                }}
                disabled={!problem.trim() || isLoading}
                className="flex-1"
                variant="outline"
              >
                {isLoading ? 'Đang vẽ...' : 'Tạo hình minh hoạ'}
              </Button>
              
              <Button 
                onClick={() => {
                  if (!problem.trim()) return;
                  setIsLoading(true);
                  setProgress(25);
                  setTimeout(() => {
                    setProgress(100);
                    setIsLoading(false);
                  }, 2000);
                }}
                disabled={!problem.trim() || isLoading}
                className="flex-1"
                variant="secondary"
              >
                {isLoading ? 'Đang tính toán...' : 'Xem đáp án'}
              </Button>
            </div>
            
            {isLoading && (
              <div className="space-y-2">
                <Progress value={progress} className="w-full" />
                <p className="text-sm text-gray-600 text-center">
                  Đang xử lý bài toán của bạn...
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  Lời giải của bạn
                </CardTitle>
                <CardDescription>
                  Viết lời giải chi tiết theo từng bước
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Bước 1: Xác định dữ liệu đã cho...
Bước 2: Áp dụng định lý Pythagore...
Bước 3: Tính toán..."
                  value={solution}
                  onChange={(e) => setSolution(e.target.value)}
                  className="min-h-40"
                />
                <div className="flex gap-3 flex-wrap">
                  <Button 
                    onClick={handleSubmitSolution}
                    disabled={!solution.trim() || isLoading}
                    className="flex-1"
                    variant="outline"
                  >
                    Kiểm tra lời giải
                  </Button>
                  
                  <Button 
                    onClick={() => {
                      if (!solution.trim()) return;
                      setIsLoading(true);
                      setProgress(25);
                      setTimeout(() => {
                        setFeedback({
                          type: 'success',
                          message: 'Tutor sẽ trả lời bạn sớm nhất có thể. Hãy tiếp tục giải bài!'
                        });
                        setProgress(100);
                        setIsLoading(false);
                      }, 1500);
                    }}
                    disabled={!solution.trim() || isLoading}
                    className="flex-1"
                    variant="secondary"
                  >
                    {isLoading ? 'Đang gửi...' : 'Hỏi tutor'}
                  </Button>
                </div>
                
                {feedback && (
                  <Alert className={feedback.type === 'success' ? 'border-green-500' : 'border-red-500'}>
                    <div className="flex items-center gap-2">
                      {feedback.type === 'success' ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500" />
                      )}
                      <AlertDescription>{feedback.message}</AlertDescription>
                    </div>
                  </Alert>
                )}
              </CardContent>
            </Card>

            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5" />
                  Hình vẽ của bài
                </CardTitle>
                <CardDescription>
                  Vùng hiển thị hình minh họa và đồ thị
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="min-h-48 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center bg-gray-50">
                  <div className="text-center text-gray-500">
                    <BookOpen className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Hình minh họa sẽ xuất hiện tại đây</p>
                    <p className="text-xs text-gray-400 mt-1">Nhấn nút "Illustrate" để tạo hình vẽ</p>
                  </div>
                </div>
                <Button 
                  onClick={() => {
                    // Simulate illustration action
                    console.log("Illustration generated");
                  }}
                  disabled={!problem.trim() || isLoading}
                  className="w-full"
                  variant="outline"
                >
                  Tạo hình minh họa
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Công cụ hỗ trợ</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="formulas" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="formulas">Công thức</TabsTrigger>
                    <TabsTrigger value="theorems">Định lý</TabsTrigger>
                  </TabsList>
                  <TabsContent value="formulas" className="space-y-2">
                    <div className="text-sm space-y-2">
                      <p><strong>Tam giác:</strong></p>
                      <p>• Diện tích = ½ × đáy × chiều cao</p>
                      <p>• Chu vi = a + b + c</p>
                      <Separator className="my-2" />
                      <p><strong>Hình tròn:</strong></p>
                      <p>• Diện tích = πr²</p>
                      <p>• Chu vi = 2πr</p>
                    </div>
                  </TabsContent>
                  <TabsContent value="theorems" className="space-y-2">
                    <div className="text-sm space-y-2">
                      <p><strong>Định lý Pythagore:</strong></p>
                      <p>a² + b² = c²</p>
                      <Separator className="my-2" />
                      <p><strong>Định lý Thales:</strong></p>
                      <p>Tỉ lệ các cạnh tương ứng</p>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5" />
                  Gợi ý giải bài
                </CardTitle>
              </CardHeader>
              <CardContent>
                {hints.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    Nhập bài toán để nhận gợi ý
                  </p>
                ) : (
                  <div className="space-y-3">
                    {hints.map((hint, index) => (
                      <div key={index} className="flex gap-3">
                        <Badge variant="outline" className="flex-shrink-0">
                          {index + 1}
                        </Badge>
                        <p className="text-sm">{hint}</p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
