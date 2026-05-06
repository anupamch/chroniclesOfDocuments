'use client';

import { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  TextField,
  Card,
  CardContent,
  Divider,
  CircularProgress,
  Alert,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import GavelIcon from '@mui/icons-material/Gavel';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import WarningIcon from '@mui/icons-material/Warning';
import ArticleIcon from '@mui/icons-material/Article';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import TimerIcon from '@mui/icons-material/Timer';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import Layout from '@/components/Layout';
import { getLegalAdvice, LegalAdviceResponse } from '@/lib/api';

export default function LegalAdvicePage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LegalAdviceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await getLegalAdvice(query);
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Failed to get legal advice. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setQuery('');
    setResult(null);
    setError(null);
  };

  return (
    <Layout>
      <Box sx={{ maxWidth: 1200, mx: 'auto', py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2, mb: 2 }}>
            <GavelIcon sx={{ fontSize: 48, color: 'primary.main' }} />
            <Typography variant="h3" component="h1" gutterBottom>
              Legal Advice
            </Typography>
          </Box>
          <Typography variant="h6" color="text.secondary">
            Get general legal guidance based on Indian law. Enter your legal question or describe your situation.
          </Typography>
        </Box>

        {/* Query Form */}
        <Paper sx={{ p: 4, mb: 4 }}>
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              multiline
              rows={4}
              variant="outlined"
              placeholder="Describe your legal issue or question...

Example: My landlord is refusing to return my security deposit of Rs. 2 lakhs even after 3 months of vacating the premises. What legal options do I have under Indian law?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
              sx={{ mb: 2 }}
            />
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                variant="outlined"
                onClick={handleClear}
                disabled={loading || (!query && !result)}
              >
                Clear
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={loading || !query.trim()}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <GavelIcon />}
              >
                {loading ? 'Analyzing...' : 'Get Legal Advice'}
              </Button>
            </Box>
          </form>
        </Paper>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 4 }}>
            {error}
          </Alert>
        )}

        {/* Results */}
        {result && (
          <Box sx={{ mb: 4 }}>
            {/* Query Summary */}
            <Card sx={{ mb: 3, backgroundColor: 'primary.50' }}>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Your Query
                </Typography>
                <Typography variant="body1">
                  {result.query_summary}
                </Typography>
                <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip
                    label={result.category.replace('_', ' ').toUpperCase()}
                    color="primary"
                    size="small"
                  />
                  {result.sources_used.map((source) => (
                    <Chip
                      key={source}
                      label={source.toUpperCase()}
                      variant="outlined"
                      size="small"
                    />
                  ))}
                  {result.processing_time_ms && (
                    <Chip
                      icon={<TimerIcon />}
                      label={`${result.processing_time_ms}ms`}
                      variant="outlined"
                      size="small"
                    />
                  )}
                </Box>
              </CardContent>
            </Card>

            {/* Main Advice */}
            <Paper sx={{ p: 4, mb: 3 }}>
              <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AccountBalanceIcon color="primary" />
                Legal Guidance
              </Typography>
              <Divider sx={{ mb: 3 }} />
              <Box
                sx={{
                  whiteSpace: 'pre-wrap',
                  lineHeight: 1.8,
                  fontSize: '1rem'
                }}
              >
                {result.advice}
              </Box>
            </Paper>

            {/* Relevant Provisions */}
            {result.relevant_provisions && result.relevant_provisions.length > 0 && (
              <Accordion defaultExpanded sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <MenuBookIcon color="primary" />
                    <Typography variant="h6">
                      Relevant Legal Provisions ({result.relevant_provisions.length})
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {result.relevant_provisions.map((provision, index) => (
                      <Grid item xs={12} md={6} key={index}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography variant="subtitle1" fontWeight="bold">
                              {provision.act}
                            </Typography>
                            <Chip label={provision.section} size="small" sx={{ mb: 1 }} />
                            {provision.title && (
                              <Typography variant="body2" color="text.secondary" gutterBottom>
                                {provision.title}
                              </Typography>
                            )}
                            <Typography variant="body2">
                              {provision.description}
                            </Typography>
                            <Chip
                              label={provision.source}
                              size="small"
                              variant="outlined"
                              sx={{ mt: 1 }}
                            />
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            )}

            {/* Case References */}
            {result.case_references && result.case_references.length > 0 && (
              <Accordion sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ArticleIcon color="primary" />
                    <Typography variant="h6">
                      Relevant Case Laws ({result.case_references.length})
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <List>
                    {result.case_references.map((caseRef, index) => (
                      <ListItem key={index} divider={index < result.case_references.length - 1}>
                        <ListItemIcon>
                          <AccountBalanceIcon fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary={caseRef.case_name}
                          secondary={
                            <Box component="span">
                              {caseRef.year && `${caseRef.year}`}
                              {caseRef.court && ` • ${caseRef.court}`}
                              {caseRef.citation && ` • ${caseRef.citation}`}
                              {caseRef.summary && (
                                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                  {caseRef.summary}
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                        <Chip label={caseRef.source} size="small" variant="outlined" />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            )}

            {/* Disclaimers */}
            <Alert
              severity="warning"
              icon={<WarningIcon />}
              sx={{ mt: 2 }}
            >
              <Typography variant="subtitle2" gutterBottom>
                Important Disclaimers
              </Typography>
              <List dense>
                {result.disclaimers.map((disclaimer, index) => (
                  <ListItem key={index} disablePadding sx={{ display: 'list-item', ml: 2 }}>
                    <ListItemIcon sx={{ minWidth: 24 }}>
                      <CheckCircleIcon fontSize="small" color="warning" />
                    </ListItemIcon>
                    <ListItemText primary={disclaimer} />
                  </ListItem>
                ))}
              </List>
            </Alert>
          </Box>
        )}

        {/* Sample Queries */}
        {!result && !loading && (
          <Paper sx={{ p: 4 }}>
            <Typography variant="h6" gutterBottom>
              Sample Legal Questions
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Click any example below to try it:
            </Typography>
            <Grid container spacing={2}>
              {[
                {
                  q: "My landlord is refusing to return my security deposit of Rs. 2 lakhs even after 3 months of vacating the premises. What legal options do I have under Indian law?",
                  category: "Property Dispute"
                },
                {
                  q: "What are the grounds for divorce under Hindu law in India?",
                  category: "Family Law"
                },
                {
                  q: "My employer hasn't paid my salary for 3 months. What legal remedies do I have under Indian labor law?",
                  category: "Labor Dispute"
                },
                {
                  q: "Someone has filed a false FIR against me. What steps should I take to protect myself under Indian criminal law?",
                  category: "Criminal Law"
                },
                {
                  q: "I purchased a defective product and the seller is refusing to replace it or refund my money. What can I do under consumer protection law?",
                  category: "Consumer Protection"
                },
                {
                  q: "What are the key provisions of the Digital Personal Data Protection Act, 2023?",
                  category: "Data Privacy"
                }
              ].map((sample, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card
                    variant="outlined"
                    sx={{
                      cursor: 'pointer',
                      '&:hover': { backgroundColor: 'action.hover' },
                      transition: 'background-color 0.2s'
                    }}
                    onClick={() => setQuery(sample.q)}
                  >
                    <CardContent>
                      <Chip label={sample.category} size="small" sx={{ mb: 1 }} />
                      <Typography variant="body2" noWrap>
                        {sample.q}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        )}
      </Box>
    </Layout>
  );
}
