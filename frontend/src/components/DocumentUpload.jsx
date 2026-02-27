import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Upload, FileText, CheckCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function DocumentUpload({ threadId }) {
  const [uploading, setUploading] = useState(false);
  const [documentType, setDocumentType] = useState('transcript');
  const [selectedFile, setSelectedFile] = useState(null);
  const [documents, setDocuments] = useState([]);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.error('File size must be less than 10MB');
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file first');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post(
        `${BACKEND_URL}/api/documents/upload/${threadId}?document_type=${documentType}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      toast.success('Document uploaded successfully');
      setSelectedFile(null);
      
      // Refresh document list
      fetchDocuments();
    } catch (error) {
      console.error('Upload failed:', error);
      toast.error('Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/documents/list/${threadId}`);
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    }
  };

  return (
    <Card className="bg-white border border-stone-100 shadow-lg">
      <CardHeader className="p-6 border-b border-stone-100">
        <CardTitle className="text-xl font-semibold">Upload Documents</CardTitle>
      </CardHeader>
      <CardContent className="p-6 space-y-6">
        {/* Upload Form */}
        <div className="space-y-4">
          <div>
            <Label htmlFor="document-type" className="text-sm font-medium text-slate-700">
              Document Type
            </Label>
            <Select value={documentType} onValueChange={setDocumentType}>
              <SelectTrigger data-testid="document-type-select" className="mt-1">
                <SelectValue placeholder="Select document type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="transcript">Official Transcript</SelectItem>
                <SelectItem value="test_scores">Test Scores (SAT/ACT)</SelectItem>
                <SelectItem value="recommendation">Recommendation Letter</SelectItem>
                <SelectItem value="essay">Personal Essay</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="file-upload" className="text-sm font-medium text-slate-700">
              Select File (PDF, JPG, PNG - Max 10MB)
            </Label>
            <div className="mt-2">
              <label
                htmlFor="file-upload"
                className="flex items-center justify-center w-full h-32 px-4 border-2 border-dashed border-stone-300 rounded-lg cursor-pointer hover:border-blue-900 hover:bg-stone-50 transition-colors"
                data-testid="file-upload-area"
              >
                <div className="text-center">
                  {selectedFile ? (
                    <div className="space-y-2">
                      <FileText className="w-10 h-10 mx-auto text-blue-900" />
                      <p className="text-sm font-medium text-slate-900">{selectedFile.name}</p>
                      <p className="text-xs text-slate-600">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Upload className="w-10 h-10 mx-auto text-slate-400" />
                      <p className="text-sm text-slate-600">Click to select a file</p>
                    </div>
                  )}
                </div>
                <input
                  id="file-upload"
                  type="file"
                  className="hidden"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={handleFileSelect}
                  data-testid="file-input"
                />
              </label>
            </div>
          </div>

          <Button
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            data-testid="upload-button"
            className="w-full bg-blue-900 text-white hover:bg-blue-800 rounded-full"
          >
            {uploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Upload Document
              </>
            )}
          </Button>
        </div>

        {/* Uploaded Documents List */}
        {documents.length > 0 && (
          <div className="pt-6 border-t border-stone-100">
            <h3 className="text-sm font-semibold text-slate-900 mb-4">Uploaded Documents</h3>
            <div className="space-y-2">
              {documents.map((doc, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-stone-50 rounded-lg"
                  data-testid={`document-${index}`}
                >
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <div>
                      <p className="text-sm font-medium text-slate-900">{doc.filename}</p>
                      <p className="text-xs text-slate-600 capitalize">
                        {doc.document_type.replace('_', ' ')}
                      </p>
                    </div>
                  </div>
                  <div className="text-xs text-slate-500">
                    {new Date(doc.uploaded_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
