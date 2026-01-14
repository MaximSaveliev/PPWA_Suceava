'use client';

import { useState, useRef } from 'react';
import { imageApi } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ImageOperation } from '@/types';
import { Upload, Download } from 'lucide-react';

export default function DashboardPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [processedUrl, setProcessedUrl] = useState<string>('');
  const [operation, setOperation] = useState<ImageOperation>('grayscale');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [width, setWidth] = useState('');
  const [height, setHeight] = useState('');
  const [x, setX] = useState('');
  const [y, setY] = useState('');
  const [angle, setAngle] = useState('');
  const [blurRadius, setBlurRadius] = useState('');
  const [keepAspectRatio, setKeepAspectRatio] = useState(true);
  const [aspectRatio, setAspectRatio] = useState(1);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setProcessedUrl('');
      setError('');
      
      // Calculate aspect ratio
      const img = new Image();
      img.onload = () => {
        setAspectRatio(img.width / img.height);
      };
      img.src = url;
    }
  };

  const handleProcess = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const params: any = {};
      if (width) params.width = parseInt(width);
      if (height) params.height = parseInt(height);
      if (x) params.x = parseInt(x);
      if (y) params.y = parseInt(y);
      if (angle) params.angle = parseInt(angle);
      if (blurRadius) params.blur_radius = parseInt(blurRadius);

      const blob = await imageApi.process(selectedFile, operation, params);
      const url = URL.createObjectURL(blob);
      setProcessedUrl(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Processing failed. Check your subscription.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (processedUrl) {
      const a = document.createElement('a');
      a.href = processedUrl;
      a.download = `processed_${selectedFile?.name}`;
      a.click();
    }
  };

  const renderOperationInputs = () => {
    switch (operation) {
      case 'crop':
        return (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>X Position</Label>
                <Input type="number" value={x} onChange={(e) => setX(e.target.value)} placeholder="0" />
              </div>
              <div className="space-y-2">
                <Label>Y Position</Label>
                <Input type="number" value={y} onChange={(e) => setY(e.target.value)} placeholder="0" />
              </div>
              <div className="space-y-2">
                <Label>Width</Label>
                <Input type="number" value={width} onChange={(e) => setWidth(e.target.value)} placeholder="500" />
              </div>
              <div className="space-y-2">
                <Label>Height</Label>
                <Input type="number" value={height} onChange={(e) => setHeight(e.target.value)} placeholder="500" />
              </div>
            </div>
          </>
        );
      case 'resize':
        return (
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="keepAspectRatio"
                checked={keepAspectRatio}
                onChange={(e) => setKeepAspectRatio(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300"
              />
              <Label htmlFor="keepAspectRatio" className="cursor-pointer">
                Keep Aspect Ratio
              </Label>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Width</Label>
                <Input 
                  type="number" 
                  value={width} 
                  onChange={(e) => {
                    setWidth(e.target.value);
                    if (keepAspectRatio && e.target.value && aspectRatio) {
                      setHeight(Math.round(parseInt(e.target.value) / aspectRatio).toString());
                    }
                  }} 
                  placeholder="800" 
                />
              </div>
              <div className="space-y-2">
                <Label>Height</Label>
                <Input 
                  type="number" 
                  value={height} 
                  onChange={(e) => {
                    setHeight(e.target.value);
                    if (keepAspectRatio && e.target.value && aspectRatio) {
                      setWidth(Math.round(parseInt(e.target.value) * aspectRatio).toString());
                    }
                  }} 
                  placeholder="600" 
                />
              </div>
            </div>
          </div>
        );
      case 'rotate':
        return (
          <div className="space-y-2">
            <Label>Angle (degrees)</Label>
            <Input type="number" value={angle} onChange={(e) => setAngle(e.target.value)} placeholder="90" />
          </div>
        );
      case 'blur':
        return (
          <div className="space-y-2">
            <Label>Blur Radius</Label>
            <Input type="number" value={blurRadius} onChange={(e) => setBlurRadius(e.target.value)} placeholder="5" />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Image Processing</h1>
        <p className="text-muted-foreground">Upload an image and apply processing operations</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card>
          <CardHeader>
            <CardTitle>Upload & Configure</CardTitle>
            <CardDescription>Select an image and choose an operation</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Select Image</Label>
              <div className="flex items-center gap-2">
                <Input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <Button
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full justify-start"
                >
                  <Upload className="mr-2 h-4 w-4 shrink-0" />
                  <span className="truncate">
                    {selectedFile 
                      ? (selectedFile.name.length > 25 
                          ? selectedFile.name.substring(0, 25) + '...' 
                          : selectedFile.name)
                      : 'Choose Image'}
                  </span>
                </Button>
              </div>
            </div>

            {previewUrl && (
              <div className="space-y-2">
                <Label>Preview</Label>
                <div className="max-h-64 overflow-hidden rounded-md border bg-gray-50 flex items-center justify-center">
                  <img src={previewUrl} alt="Preview" className="max-h-64 w-auto object-contain" />
                </div>
              </div>
            )}

            <div className="space-y-2">
              <Label>Operation</Label>
              <Select value={operation} onValueChange={(v) => setOperation(v as ImageOperation)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="grayscale">Grayscale</SelectItem>
                  <SelectItem value="sepia">Sepia</SelectItem>
                  <SelectItem value="crop">Crop</SelectItem>
                  <SelectItem value="resize">Resize</SelectItem>
                  <SelectItem value="rotate">Rotate</SelectItem>
                  <SelectItem value="blur">Blur</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {renderOperationInputs()}

            {error && (
              <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">
                {error}
              </div>
            )}

            <Button onClick={handleProcess} disabled={loading || !selectedFile} className="w-full">
              {loading ? 'Processing...' : 'Process Image'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Result</CardTitle>
            <CardDescription>Your processed image will appear here</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {processedUrl ? (
              <>
                <div className="max-h-96 overflow-hidden rounded-md border bg-gray-50 flex items-center justify-center">
                  <img src={processedUrl} alt="Processed" className="max-h-96 w-auto object-contain" />
                </div>
                <Button onClick={handleDownload} className="w-full">
                  <Download className="mr-2 h-4 w-4" />
                  Download Image
                </Button>
              </>
            ) : (
              <div className="flex items-center justify-center h-64 border-2 border-dashed rounded-md">
                <p className="text-muted-foreground">Processed image will appear here</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
