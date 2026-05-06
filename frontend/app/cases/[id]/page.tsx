'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Alert,
  Card,
  CardContent,
  Divider,
  CircularProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RefreshIcon from '@mui/icons-material/Refresh';
import DescriptionIcon from '@mui/icons-material/Description';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ErrorIcon from '@mui/icons-material/Error';
import PendingIcon from '@mui/icons-material/Pending';
import TimelineIcon from '@mui/icons-material/Timeline';
import DeleteIcon from '@mui/icons-material/Delete';
import DownloadIcon from '@mui/icons-material/Download';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import GavelIcon from '@mui/icons-material/Gavel';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import Layout from '@/components/Layout';
import FileUploadDialog from '@/components/FileUploadDialog';
import { getCase, getCaseDocuments, startScan, getScanStatus, Case, Document, ScanStatus, TimelineEvent, deleteCase, deleteDocument, getDocumentViewUrl } from '@/lib/api';
import { getLegalAdvice, LegalAdviceResponse } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { saveAs } from 'file-saver';
import { Document as DocxDocument, Packer, Paragraph, TextRun } from 'docx';

export default function CaseDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, loading: authLoading } = useAuth();
  const caseId = params.id as string;
  const fromSidebar = searchParams.get('from') === 'sidebar';

  const [caseDetails, setCaseDetails] = useState<Case | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [scanStatus, setScanStatus] = useState<ScanStatus | null>(null);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [deletingDocId, setDeletingDocId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [legalAdviceOpen, setLegalAdviceOpen] = useState(false);
  const [legalQuery, setLegalQuery] = useState('');
  const [legalAdvice, setLegalAdvice] = useState<LegalAdviceResponse | null>(null);
  const [legalAdviceLoading, setLegalAdviceLoading] = useState(false);
  const [legalAdviceError, setLegalAdviceError] = useState<string | null>(null);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [notificationOpen, setNotificationOpen] = useState(false);

  useEffect(() => {
    if (!authLoading && user && caseId) {
      const controller = new AbortController();
      fetchData(controller.signal);

      // Establish WebSocket connection for real-time updates
      const clientId = `user_${user.user_id || 'guest'}_${Math.random().toString(36).substr(2, 9)}`;
      const wsUrl = `ws://${window.location.hostname}:8000/api/ws/${clientId}`;
      const socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        console.log('[WS] Connected successfully');
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('[WS] Received:', data.type, data);

          if (data.type === 'scan_complete' && data.case_id === caseId) {
            console.log('[WS] Analysis complete for case:', caseId);
            // Mark analysis as complete
            setAnalysisComplete(true);
            setNotificationOpen(true);
            // Update case details with completed status
            setCaseDetails(prev => prev ? { ...prev, analysis_status: 'completed' } : null);
            // Automatically refresh UI to show results
            setTimeout(() => fetchData(), 500);
          } else if (data.type === 'document_processed' && data.case_id === caseId) {
            console.log('[WS] Document processed');
            // Update status silently
            getScanStatus(caseId).then(setScanStatus);
          }
        } catch (err) {
          console.error('[WS] Error parsing message:', err);
        }
      };

      socket.onerror = (error) => {
        console.error('[WS] WebSocket error:', error);
      };

      socket.onclose = () => {
        console.log('[WS] Disconnected');
      };

      return () => {
        controller.abort();
        socket.close();
      };
    }
  }, [caseId, authLoading, user]);

  const fetchData = async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);

    try {
      // Always fetch fresh case data to ensure we have latest info
      const caseData = await getCase(caseId);
      setCaseDetails(caseData);

      // Fetch documents for this case
      const docsData = await getCaseDocuments(caseId);
      setDocuments(docsData);

      // Fetch scan status only if there are documents
      if (docsData && docsData.length > 0) {
        const statusData = await getScanStatus(caseId, signal);
        setScanStatus(statusData);
      }
    } catch (err: any) {
      if (err.name !== 'AbortError' && err.name !== 'CanceledError') {
        setError(err.message || 'Failed to load case details');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUploadClick = () => {
    setUploadDialogOpen(true);
  };

  const handleUploadComplete = () => {
    setUploadDialogOpen(false);
    fetchData(); // Refresh data after upload
  };

  const handleStartScan = async () => {
    // Prevent multiple scans
    if (caseDetails?.analysis_status === 'in_progress' || scanning || analysisComplete === false && caseDetails?.analysis_status === 'in_progress') {
      return;
    }
    
    setScanning(true);
    setAnalysisComplete(false);
    setError(null);
    
    try {
      console.log('Starting scan for case:', caseId);
      await startScan(caseId);
      // Update local state to reflect scanning started
      setCaseDetails(prev => prev ? { ...prev, analysis_status: 'in_progress' } : null);
      console.log('Scan request sent, waiting for websocket notification...');
      // The websocket will notify when complete
    } catch (err: any) {
      setError(err.message || 'Failed to start scan');
      setScanning(false);
      setAnalysisComplete(false);
    }
  };

  const handleRefresh = () => {
    fetchData();
  };

  const handleDeleteCase = async () => {
    if (!window.confirm('Are you sure you want to delete this case? All associated documents will be permanently deleted.')) {
      return;
    }

    setDeleting(true);
    try {
      await deleteCase(caseId);
      router.push('/cases/list');
    } catch (err: any) {
      setError(err.message || 'Failed to delete case');
      setDeleting(false);
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    if (!window.confirm('Are you sure you want to permanently delete this document?')) {
      return;
    }

    setDeletingDocId(documentId);
    try {
      await deleteDocument(caseId, documentId);
      fetchData(); // Refresh to update list and counts
    } catch (err: any) {
      setError(err.message || 'Failed to delete document');
    } finally {
      setDeletingDocId(null);
    }
  };

  const getTimelineText = () => {
    let text = `Timeline Analysis: ${caseDetails?.title || caseDetails?.case_number}\n\n`;

    // Add structured events
    const allEvents: TimelineEvent[] = [];
    if (scanStatus?.results) {
      scanStatus.results.forEach(result => {
        if (result.timeline_events && Array.isArray(result.timeline_events)) {
          allEvents.push(...result.timeline_events);
        }
      });
    }

    if (allEvents.length > 0) {
      const sortedEvents = allEvents.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

      let currentDate = '';
      sortedEvents.forEach(event => {
        if (event.date !== currentDate) {
          currentDate = event.date;
          text += `\n${new Date(event.date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}\n`;
          text += `--------------------------------------------------\n`;
        }
        text += `• [${event.type.toUpperCase()}] ${event.event} (Source: ${event.source})\n`;
      });
      text += `\n\n`;
    }

    if (caseDetails?.timeline_story) {
      text += `Summary Story:\n`;
      text += `--------------------------------------------------\n`;
      text += `${caseDetails.timeline_story}\n`;
    }

    return text || 'No timeline data available.';
  };

  const handleExportPDF = async () => {
    try {
      const { jsPDF } = await import('jspdf');
      const doc = new jsPDF();
      const text = getTimelineText();

      const lines = doc.splitTextToSize(text, 180);
      let y = 15;

      lines.forEach((line: string) => {
        if (y > 280) {
          doc.addPage();
          y = 15;
        }
        doc.text(line, 15, y);
        y += 7;
      });

      doc.save(`Timeline_${caseDetails?.case_number || 'export'}.pdf`);
    } catch (error) {
      console.error('Failed to export PDF:', error);
      alert('Failed to export PDF');
    }
  };

  const handleExportDocx = async () => {
    try {
      const text = getTimelineText();
      const paragraphs = text.split('\n').map(line =>
        new Paragraph({
          children: [new TextRun(line)],
        })
      );

      const doc = new DocxDocument({
        sections: [{
          properties: {},
          children: paragraphs,
        }],
      });

      const blob = await Packer.toBlob(doc);
      saveAs(blob, `Timeline_${caseDetails?.case_number || 'export'}.docx`);
    } catch (error) {
      console.error('Failed to export DOCX:', error);
      alert('Failed to export DOCX');
    }
  };

  const handleOpenLegalAdvice = () => {
    setLegalAdviceOpen(true);
    setLegalAdvice(null);
    setLegalAdviceError(null);
    // Pre-fill with timeline story context if available
    if (caseDetails?.timeline_story) {
      setLegalQuery(`Based on the case timeline: ${caseDetails.timeline_story.substring(0, 500)}...`);
    }
  };

  const handleGetLegalAdvice = async () => {
    if (!legalQuery.trim()) return;

    setLegalAdviceLoading(true);
    setLegalAdviceError(null);

    try {
      const response = await getLegalAdvice(
        legalQuery,
        'en',
        caseDetails?.timeline_story || undefined,
        caseDetails?.case_number,
        caseDetails?.title
      );
      setLegalAdvice(response);
    } catch (err: any) {
      setLegalAdviceError(err.message || 'Failed to get legal advice');
    } finally {
      setLegalAdviceLoading(false);
    }
  };

  const handleCloseLegalAdvice = () => {
    setLegalAdviceOpen(false);
    setLegalQuery('');
    setLegalAdvice(null);
    setLegalAdviceError(null);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon color="success" fontSize="small" />;
      case 'failed':
        return <ErrorIcon color="error" fontSize="small" />;
      case 'processing':
        return <PendingIcon color="warning" fontSize="small" />;
      default:
        return <PendingIcon color="disabled" fontSize="small" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'processing':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  if (loading) {
    return (
      <Layout>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  if (error || !caseDetails) {
    return (
      <Layout>
        <Alert severity="error">{error || 'Case not found'}</Alert>
      </Layout>
    );
  }

  const progress = scanStatus ? (scanStatus.processed_documents / scanStatus.total_documents) * 100 : 0;

  return (
    <Layout>
      <Box>
        {/* Header */}
        <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton
            onClick={() => router.push('/cases/list')}
            sx={{
              color: 'text.secondary',
              '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.04)' }
            }}
          >
            <ArrowBackIcon fontSize="large" />
          </IconButton>
          <Box>
            <Typography
              variant="h4"
              component="h1"
              gutterBottom
              sx={{
                mb: 0,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                maxWidth: '800px'
              }}
            >
              {caseDetails.case_number}
            </Typography>
            <Typography
              variant="h6"
              color="text.secondary"
              sx={{
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                maxWidth: '800px'
              }}
            >
              {caseDetails.title}
            </Typography>
          </Box>
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          {caseDetails.description}
        </Typography>

        {/* Actions */}
        <Box sx={{ display: 'flex', gap: 2, mb: 3, alignItems: 'center', flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            startIcon={<UploadFileIcon />}
            onClick={handleUploadClick}
            sx={{ textTransform: 'none' }}
          >
            Upload Documents
          </Button>
          <Button
            variant="outlined"
            startIcon={caseDetails?.analysis_status === 'in_progress' ? <CircularProgress size={20} /> : <PlayArrowIcon />}
            onClick={handleStartScan}
            disabled={scanning || documents.length === 0 || caseDetails?.analysis_status === 'in_progress'}
            sx={{ textTransform: 'none' }}
          >
            {caseDetails?.analysis_status === 'in_progress' ? '🔄 Analysis in Progress...' : scanning ? 'Starting...' : 'Start Scan'}
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            sx={{ textTransform: 'none' }}
          >
            Refresh
          </Button>
          <Box sx={{ flexGrow: 1 }} />
          <Button
            variant="outlined"
            color="error"
            startIcon={deleting ? <CircularProgress size={20} color="inherit" /> : <DeleteIcon />}
            onClick={handleDeleteCase}
            disabled={deleting}
            sx={{ textTransform: 'none' }}
          >
            Delete Case
          </Button>
        </Box>

        {/* Analysis Complete Notification */}
        {analysisComplete && notificationOpen && (
          <Alert 
            severity="success" 
            onClose={() => setNotificationOpen(false)}
            sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}
          >
            <CheckCircleIcon fontSize="small" />
            ✨ Analysis complete! Your timeline has been generated successfully.
          </Alert>
        )}

        {/* Scan Progress */}
        {scanStatus && scanStatus.status !== 'not_started' && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Scan Progress
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box sx={{ width: '100%', mr: 1 }}>
                  <LinearProgress variant="determinate" value={progress} />
                </Box>
                <Box sx={{ minWidth: 35 }}>
                  <Typography variant="body2" color="text.secondary">
                    {Math.round(progress)}%
                  </Typography>
                </Box>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={3}>
                  <Typography variant="body2" color="text.secondary">
                    Total
                  </Typography>
                  <Typography variant="h6">{scanStatus.total_documents}</Typography>
                </Grid>
                <Grid item xs={3}>
                  <Typography variant="body2" color="text.secondary">
                    Processed
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    {scanStatus.processed_documents}
                  </Typography>
                </Grid>
                <Grid item xs={3}>
                  <Typography variant="body2" color="text.secondary">
                    Pending
                  </Typography>
                  <Typography variant="h6" color="warning.main">
                    {scanStatus.pending_documents}
                  </Typography>
                </Grid>
                <Grid item xs={3}>
                  <Typography variant="body2" color="text.secondary">
                    Failed
                  </Typography>
                  <Typography variant="h6" color="error.main">
                    {scanStatus.failed_documents}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}

        {/* Timeline Display */}
        {(scanStatus?.results && scanStatus.results.length > 0) || caseDetails?.timeline_story ? (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TimelineIcon color="primary" />
                  Timeline Analysis
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={handleExportPDF}
                    startIcon={<DownloadIcon />}
                  >
                    Export PDF
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={handleExportDocx}
                    startIcon={<DownloadIcon />}
                  >
                    Export DOCX
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={handleOpenLegalAdvice}
                    startIcon={<GavelIcon />}
                    disabled={!caseDetails?.timeline_story && !scanStatus?.results?.length}
                  >
                    Get Legal Advice
                  </Button>
                </Box>
              </Box>
              <Divider sx={{ mb: 2 }} />

              {/* Try to show chronological events first */}
              {(() => {
                // Collect all timeline events from all scan results
                const allEvents: TimelineEvent[] = [];
                if (scanStatus?.results) {
                  scanStatus.results.forEach(result => {
                    if (result.timeline_events && Array.isArray(result.timeline_events)) {
                      allEvents.push(...result.timeline_events);
                    }
                  });
                }

                // Sort by date (oldest first)
                const sortedEvents = allEvents.sort((a, b) => {
                  const dateA = new Date(a.date);
                  const dateB = new Date(b.date);
                  return dateA.getTime() - dateB.getTime();
                });

                // If we have timeline events, show them
                if (sortedEvents.length > 0) {
                  // Group events by date
                  const eventsByDate: { [date: string]: TimelineEvent[] } = {};
                  sortedEvents.forEach(event => {
                    if (!eventsByDate[event.date]) {
                      eventsByDate[event.date] = [];
                    }
                    eventsByDate[event.date].push(event);
                  });

                  return (
                    <Box sx={{ position: 'relative' }}>
                      {/* Timeline line */}
                      <Box sx={{
                        position: 'absolute',
                        left: 16,
                        top: 0,
                        bottom: 0,
                        width: 2,
                        backgroundColor: 'primary.light',
                        zIndex: 0
                      }} />

                      {/* Events by date */}
                      {Object.entries(eventsByDate).map(([date, events], dateIndex) => (
                        <Box key={date} sx={{ position: 'relative', mb: 3, pl: 4 }}>
                          {/* Date marker */}
                          <Box sx={{
                            position: 'absolute',
                            left: 8,
                            top: 0,
                            width: 16,
                            height: 16,
                            borderRadius: '50%',
                            backgroundColor: 'primary.main',
                            zIndex: 1,
                            border: '2px solid white'
                          }} />

                          {/* Date header */}
                          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                            {new Date(date).toLocaleDateString('en-US', {
                              weekday: 'long',
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric'
                            })}
                          </Typography>

                          {/* Events for this date */}
                          {events.map((event, eventIndex) => (
                            <Paper
                              key={`${date}-${eventIndex}`}
                              elevation={1}
                              sx={{
                                p: 2,
                                mb: 1,
                                backgroundColor: 'white',
                                borderLeft: '3px solid',
                                borderLeftColor: event.type === 'financial' ? 'success.main' :
                                  event.type === 'legal' ? 'warning.main' :
                                    event.type === 'medical' ? 'error.main' :
                                      'primary.main',
                              }}
                            >
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                                <Typography variant="body1" sx={{ fontWeight: 500 }}>
                                  {event.event}
                                </Typography>
                                <Chip
                                  label={event.type}
                                  size="small"
                                  variant="outlined"
                                  sx={{
                                    textTransform: 'capitalize',
                                    backgroundColor: '#d4d3d3ff',
                                  }}
                                />
                              </Box>
                              <Typography variant="caption" color="text.secondary">
                                Source: {event.source}
                              </Typography>
                            </Paper>
                          ))}
                        </Box>
                      ))}
                    </Box>
                  );
                }
                // If no timeline events but we have a story, show the story
                else if (caseDetails?.timeline_story) {
                  return (
                    <Paper
                      elevation={0}
                      sx={{
                        p: 3,
                        backgroundColor: 'grey.50',
                        maxHeight: '500px',
                        overflow: 'auto',
                        fontFamily: 'monospace',
                        whiteSpace: 'pre-wrap',
                        fontSize: '0.875rem',
                        lineHeight: 1.6
                      }}
                    >
                      {caseDetails.timeline_story}
                    </Paper>
                  );
                }
                // If neither timeline events nor story
                else {
                  return (
                    <Paper sx={{ p: 3, textAlign: 'center', backgroundColor: 'grey.50' }}>
                      <Typography variant="body2" color="text.secondary">
                        No timeline analysis available yet. Start a scan to analyze documents.
                      </Typography>
                    </Paper>
                  );
                }
              })()}
            </CardContent>
          </Card>
        ) : null}

        {/* Documents Table */}
        <Paper>
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Documents ({Array.isArray(documents) ? documents.length : 0})</Typography>
          </Box>
          <Divider />
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>File Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Uploaded</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {!Array.isArray(documents) || documents.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Box sx={{ py: 4 }}>
                        <DescriptionIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
                        <Typography variant="body1" color="text.secondary">
                          No documents uploaded yet
                        </Typography>
                        <Button
                          variant="outlined"
                          startIcon={<UploadFileIcon />}
                          onClick={handleUploadClick}
                          sx={{ mt: 2, textTransform: 'none' }}
                        >
                          Upload Documents
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ) : (
                  Array.isArray(documents) && documents.map((doc) => (
                    <TableRow key={doc.document_id} hover>
                      <TableCell sx={{ maxWidth: 300 }}>
                        <Box sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1,
                        }}>
                          <DescriptionIcon fontSize="small" color="action" />
                          <Typography
                            variant="body2"
                            sx={{
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap'
                            }}
                          >
                            {doc.file_name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{doc.file_type}</TableCell>
                      <TableCell>{formatFileSize(doc.file_size)}</TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(doc.status)}
                          label={doc.status}
                          size="small"
                          color={getStatusColor(doc.status) as any}
                          sx={{ textTransform: 'capitalize' }}
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(doc.uploaded_at).toLocaleString()}
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                          <IconButton
                            size="small"
                            color="primary"
                            title="Download/View Document"
                            onClick={() => {
                              const token = localStorage.getItem('token');
                              window.open(`${getDocumentViewUrl(caseId, doc.document_id)}?token=${token}&download=true`, '_blank');
                            }}
                          >
                            <DownloadIcon fontSize="small" />
                          </IconButton>
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeleteDocument(doc.document_id)}
                            disabled={deletingDocId === doc.document_id}
                          >
                            {deletingDocId === doc.document_id ? (
                              <CircularProgress size={20} />
                            ) : (
                              <DeleteIcon fontSize="small" />
                            )}
                          </IconButton>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Box>

      {/* Upload Dialog */}
      <FileUploadDialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        caseId={caseId}
      />

      {/* Legal Advice Dialog */}
      <Dialog
        open={legalAdviceOpen}
        onClose={handleCloseLegalAdvice}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { minHeight: '60vh' }
        }}
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <GavelIcon color="primary" />
          Legal Advice for Case: {caseDetails?.case_number}
        </DialogTitle>
        <DialogContent dividers>
          {!legalAdvice ? (
            <>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Describe your legal question or concern regarding this case. The system will analyze the timeline and provide legal guidance.
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Your Legal Question"
                placeholder="Example: What legal options do I have based on this case timeline? What sections of law apply?"
                value={legalQuery}
                onChange={(e) => setLegalQuery(e.target.value)}
                disabled={legalAdviceLoading}
                sx={{ mb: 2 }}
              />
              {legalAdviceError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {legalAdviceError}
                </Alert>
              )}
            </>
          ) : (
            <Box>
              {/* Category & Summary */}
              <Box sx={{ mb: 3 }}>
                <Chip
                  label={legalAdvice.category.replace('_', ' ').toUpperCase()}
                  color="primary"
                  size="small"
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  {legalAdvice.query_summary}
                </Typography>
              </Box>

              {/* Main Advice */}
              <Paper variant="outlined" sx={{ p: 2, mb: 3, backgroundColor: '#f8f9fa' }}>
                <Typography variant="h6" gutterBottom>
                  Legal Guidance
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Box sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
                  {legalAdvice.advice}
                </Box>
              </Paper>

              {/* Relevant Provisions */}
              {legalAdvice.relevant_provisions?.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Relevant Legal Provisions
                  </Typography>
                  {legalAdvice.relevant_provisions.map((provision, index) => (
                    <Card key={index} variant="outlined" sx={{ mb: 1 }}>
                      <CardContent sx={{ py: 1.5 }}>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {provision.act} - {provision.section}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {provision.description?.substring(0, 200)}...
                        </Typography>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              )}

              {/* Case References */}
              {legalAdvice.case_references?.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Relevant Case Laws
                  </Typography>
                  {legalAdvice.case_references.map((caseRef, index) => (
                    <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
                      • {caseRef.case_name} {caseRef.year && `(${caseRef.year})`}
                    </Typography>
                  ))}
                </Box>
              )}

              {/* Disclaimers */}
              <Alert severity="warning">
                <Typography variant="subtitle2" gutterBottom>
                  Important Disclaimers
                </Typography>
                {legalAdvice.disclaimers.map((disclaimer, index) => (
                  <Typography key={index} variant="body2">
                    • {disclaimer}
                  </Typography>
                ))}
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          {!legalAdvice ? (
            <>
              <Button onClick={handleCloseLegalAdvice}>Cancel</Button>
              <Button
                variant="contained"
                onClick={handleGetLegalAdvice}
                disabled={legalAdviceLoading || !legalQuery.trim()}
                startIcon={legalAdviceLoading ? <CircularProgress size={20} /> : <GavelIcon />}
              >
                {legalAdviceLoading ? 'Analyzing...' : 'Get Advice'}
              </Button>
            </>
          ) : (
            <Button onClick={handleCloseLegalAdvice}>Close</Button>
          )}
        </DialogActions>
      </Dialog>
    </Layout>
  );
}
