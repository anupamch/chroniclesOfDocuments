'use client';

import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Alert,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import { createCase } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

export default function NewCasePage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [formData, setFormData] = useState({
    case_number: '',
    title: '',
    description: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.case_number || !formData.title) {
      setError('Case number and title are required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await createCase(formData);
      router.push(`/cases/${result.case_id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create case');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Box>
        <Typography variant="h4" component="h1" gutterBottom>
          Create New Case
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Create a new case to organize and analyze your documents
        </Typography>

        <Paper sx={{ p: 4, maxWidth: 800 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Case Number"
              name="case_number"
              value={formData.case_number}
              onChange={handleChange}
              required
              placeholder="e.g., CASE-2024-001"
              helperText="Unique identifier for this case (alphanumeric, hyphens, underscores)"
              sx={{ mb: 3 }}
            />

            <TextField
              fullWidth
              label="Title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              placeholder="e.g., Contract Dispute - ABC Corp"
              helperText="Brief title describing the case"
              sx={{ mb: 3 }}
            />

            <TextField
              fullWidth
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              multiline
              rows={4}
              placeholder="Detailed description of the case..."
              helperText="Optional detailed description"
              sx={{ mb: 3 }}
            />

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                type="submit"
                variant="contained"
                startIcon={<SaveIcon />}
                disabled={loading}
                sx={{ textTransform: 'none' }}
              >
                {loading ? 'Creating...' : 'Create Case'}
              </Button>
              <Button
                variant="outlined"
                onClick={() => router.back()}
                disabled={loading}
                sx={{ textTransform: 'none' }}
              >
                Cancel
              </Button>
            </Box>
          </form>
        </Paper>
      </Box>
    </Layout>
  );
}
