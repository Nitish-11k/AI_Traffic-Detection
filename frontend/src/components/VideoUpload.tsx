import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  Video, 
  Play, 
  Pause, 
  RotateCcw, 
  AlertCircle,
  CheckCircle,
  Loader2,
  FileVideo,
  Trash2
} from 'lucide-react';
import ReactPlayer from 'react-player';
import { motion } from 'framer-motion';
import { apiService, UploadResponse } from '../services/api';
import toast from 'react-hot-toast';

const VideoUpload: React.FC = () => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [videoUrl, setVideoUrl] = useState<string>('');
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [detectionFrame, setDetectionFrame] = useState<string>('');
  const [detectionFrameNumber, setDetectionFrameNumber] = useState(0);
  const [totalViolations, setTotalViolations] = useState(0);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [wsConnected, setWsConnected] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file && file.type.startsWith('video/')) {
      setUploadedFile(file);
      setVideoUrl(URL.createObjectURL(file));
      setResult(null);
      toast.success('Video uploaded successfully!');
    } else {
      toast.error('Please upload a valid video file');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
    },
    multiple: false,
    maxSize: 100 * 1024 * 1024 // 100MB
  });

  const handleProcessVideo = async () => {
    if (!uploadedFile) return;

    setProcessing(true);
    setDetectionFrame('');
    setTotalViolations(0);
    
    try {
      // Connect to WebSocket for real-time updates
      const websocket = new WebSocket('ws://localhost:8000/ws');
      setWs(websocket);
      
      websocket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('WebSocket message received:', message.type);
          if (message.type === 'frame') {
            console.log('Frame received:', message.data.frame_number, 'Violations:', message.data.total_violations);
            setDetectionFrame(`data:image/jpeg;base64,${message.data.frame_data}`);
            setDetectionFrameNumber(message.data.frame_number);
            setTotalViolations(message.data.total_violations);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      websocket.onopen = () => {
        console.log('WebSocket connected');
        setWsConnected(true);
      };
      
      websocket.onclose = () => {
        console.log('WebSocket disconnected');
        setWs(null);
        setWsConnected(false);
      };

      const formData = new FormData();
      formData.append('file', uploadedFile);

      // Show processing message
      toast.loading('Processing video... This may take a few minutes.', {
        duration: 10000,
      });

      const response = await apiService.uploadVideo(formData);
      // Ensure violations array exists
      const resultWithViolations = {
        ...response,
        violations: response.violations || []
      };
      setResult(resultWithViolations);
      
      if (response.total_violations > 0) {
        toast.success(`Processing complete! Found ${response.total_violations} violations.`);
      } else {
        toast.success('Processing complete! No violations detected.');
      }
    } catch (error: any) {
      console.error('Error processing video:', error);
      
      // More specific error messages
      if (error.code === 'ECONNABORTED') {
        toast.error('Video processing timed out. Please try with a shorter video.');
      } else if (error.response?.status === 413) {
        toast.error('Video file is too large. Please use a smaller video.');
      } else if (error.response?.data?.message) {
        toast.error(`Error: ${error.response.data.message}`);
      } else {
        toast.error('Error processing video. Please try again.');
      }
    } finally {
      setProcessing(false);
      if (ws) {
        ws.close();
        setWs(null);
      }
    }
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    setVideoUrl('');
    setResult(null);
    setCurrentTime(0);
    setDuration(0);
    setPlaying(false);
  };

  const getViolationTypeColor = (type: string) => {
    switch (type) {
      case 'red_light': return 'bg-danger-100 text-danger-800 border-danger-200';
      case 'wrong_side': return 'bg-warning-100 text-warning-800 border-warning-200';
      case 'no_helmet': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getViolationTypeLabel = (type: string) => {
    switch (type) {
      case 'red_light': return 'Red Light Violation';
      case 'wrong_side': return 'Wrong Side Driving';
      case 'no_helmet': return 'No Helmet';
      default: return type;
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const seekToViolation = (frameNumber: number) => {
    // Assuming 30 FPS, calculate time from frame number
    const timeInSeconds = frameNumber / 30;
    setCurrentTime(timeInSeconds);
    setPlaying(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Video Upload & Analysis</h1>
        <p className="text-gray-600 mt-1">Upload traffic videos for AI-powered violation detection</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="space-y-6">
          {/* Upload Area */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Video</h3>
            
            {!uploadedFile ? (
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-primary-400 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">
                  {isDragActive ? 'Drop the video here' : 'Drag & drop a video file'}
                </p>
                <p className="text-gray-500 mb-4">or click to browse</p>
                <p className="text-sm text-gray-400">
                  Supports MP4, AVI, MOV, MKV, WMV (max 100MB)
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <FileVideo className="w-8 h-8 text-primary-600" />
                    <div>
                      <p className="font-medium text-gray-900">{uploadedFile.name}</p>
                      <p className="text-sm text-gray-500">
                        {(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={handleRemoveFile}
                    className="p-2 text-gray-400 hover:text-danger-600 transition-colors"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>

                <button
                  onClick={handleProcessVideo}
                  disabled={processing}
                  className="w-full btn-primary flex items-center justify-center space-x-2"
                >
                  {processing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : (
                    <>
                      <Video className="w-5 h-5" />
                      <span>Analyze Video</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Results Summary */}
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Results</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {result.total_violations > 0 ? (
                      <AlertCircle className="w-8 h-8 text-danger-600" />
                    ) : (
                      <CheckCircle className="w-8 h-8 text-success-600" />
                    )}
                    <div>
                      <p className="font-medium text-gray-900">
                        {result.total_violations > 0 ? 'Violations Detected' : 'No Violations'}
                      </p>
                      <p className="text-sm text-gray-500">
                        {result.total_violations} violation{result.total_violations !== 1 ? 's' : ''} found
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-gray-900">{result.total_violations}</p>
                  </div>
                </div>

                {result.violations && result.violations.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-medium text-gray-900">Violation Types:</h4>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(
                        result.violations.reduce((acc, v) => {
                          acc[v.type] = (acc[v.type] || 0) + 1;
                          return acc;
                        }, {} as Record<string, number>)
                      ).map(([type, count]) => (
                        <span
                          key={type}
                          className={`px-3 py-1 rounded-full text-sm font-medium border ${getViolationTypeColor(type)}`}
                        >
                          {getViolationTypeLabel(type)}: {count}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </div>

        {/* Video Player Section */}
        <div className="space-y-6">
          {/* Real-time Detection Display */}
          {processing && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Real-time Detection</h3>
              <div className="space-y-4">
                {/* Connection Status */}
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="text-sm text-gray-600">
                    {wsConnected ? 'Connected to detection stream' : 'Connecting...'}
                  </span>
                </div>
                
                {/* Detection Frame */}
                {detectionFrame ? (
                  <div className="relative bg-black rounded-lg overflow-hidden">
                    <img 
                      src={detectionFrame} 
                      alt="Detection Frame" 
                      className="w-full h-auto transition-opacity duration-100"
                      style={{ 
                        maxHeight: '400px',
                        animation: 'fadeIn 0.1s ease-in-out'
                      }}
                      key={detectionFrameNumber} // Force re-render for smooth transition
                    />
                    {/* Video-like overlay */}
                    <div className="absolute top-2 right-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
                      LIVE
                    </div>
                  </div>
                ) : (
                  <div className="bg-gray-100 rounded-lg p-8 text-center">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2 text-gray-400" />
                    <p className="text-gray-600">Waiting for detection frames...</p>
                  </div>
                )}
                
                {/* Frame Info */}
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>Frame: {detectionFrameNumber}</span>
                  <span>Total Violations: {totalViolations}</span>
                </div>
              </div>
            </div>
          )}

          {/* Video Player */}
          {videoUrl && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Video Preview</h3>
              
              <div className="space-y-4">
                <div className="relative bg-black rounded-lg overflow-hidden">
                  <ReactPlayer
                    url={videoUrl}
                    width="100%"
                    height="300px"
                    playing={playing}
                    onProgress={({ playedSeconds }) => setCurrentTime(playedSeconds)}
                    onDuration={setDuration}
                    controls={true}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setPlaying(!playing)}
                      className="p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                    >
                      {playing ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    </button>
                    <span className="text-sm text-gray-600">
                      {formatTime(currentTime)} / {formatTime(duration)}
                    </span>
                  </div>
                  
                  <button
                    onClick={() => {
                      setCurrentTime(0);
                      setPlaying(false);
                    }}
                    className="p-2 text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Violations List */}
          {result && result.violations && result.violations.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Detected Violations</h3>
              
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {result.violations.map((violation, index) => (
                  <motion.div
                    key={violation.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                    onClick={() => seekToViolation(violation.frame_number)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: getViolationTypeColor(violation.type).includes('danger') ? '#ef4444' : 
                                   getViolationTypeColor(violation.type).includes('warning') ? '#f59e0b' : '#8b5cf6' }}
                        ></div>
                        <div>
                          <p className="font-medium text-gray-900">
                            {getViolationTypeLabel(violation.type)}
                          </p>
                          <p className="text-sm text-gray-500">
                            Frame {violation.frame_number} • Confidence: {(violation.confidence * 100).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">
                          {formatTime(violation.frame_number / 30)}
                        </p>
                        <p className="text-xs text-gray-500">
                          ID: {violation.vehicle_id}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoUpload;

