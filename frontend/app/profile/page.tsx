'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { updateProfile } from '@/lib/api';
import { 
  Container, 
  Typography, 
  Paper, 
  Box,
  TextField,
  Button,
  Alert,
  CircularProgress
} from '@mui/material';
import Layout from '@/components/Layout';

export default function ProfilePage() {
  const { user, loading, loginState } = useAuth();
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (user) {
      setFullName(user.full_name);
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsSaving(true);

    try {
      const updateData: any = { full_name: fullName };
      if (password) {
        updateData.password = password;
      }
      
      await updateProfile(updateData);
      setSuccess('Profile updated successfully');
      setPassword(''); // Clear password field
      // We don't have a loginState updater that doesn't push route, but the auth context
      // will fetch the updated user on the next page load. For now, it's fine.
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container maxWidth="sm" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Profile Management
        </Typography>
        
        <Paper elevation={3} sx={{ p: 4, mt: 3, borderRadius: 2 }}>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              margin="normal"
              fullWidth
              label="Email Address"
              value={user?.email || ''}
              disabled
              helperText="Email cannot be changed"
            />
            <TextField
              margin="normal"
              required
              fullWidth
              label="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
            <TextField
              margin="normal"
              fullWidth
              label="New Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              helperText="Leave blank to keep your current password"
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3 }}
              disabled={isSaving}
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </Button>
          </Box>
        </Paper>
      </Container>
    </Layout>
  );
}
