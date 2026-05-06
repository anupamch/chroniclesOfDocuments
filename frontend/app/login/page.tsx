'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { login, loginWithEmailOrPhone } from '@/lib/api';
import { 
  Container, 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Alert, 
  Paper, 
  Link as MuiLink,
  InputAdornment,
  IconButton
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import Link from 'next/link';

export default function LoginPage() {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [helperText, setHelperText] = useState('Enter email or phone number');
  const [isClient, setIsClient] = useState(false);
  const { loginState } = useAuth();

  // Regex patterns for email and phone detection
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const phoneRegex = /^[\+]?[0-9]{10,15}$/;

  const detectIdentifierType = (value: string): 'email' | 'phone' | 'unknown' => {
    if (emailRegex.test(value)) return 'email';
    if (phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''))) return 'phone';
    return 'unknown';
  };

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  // Initialize client-side state
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Update helper text only on client side
  useEffect(() => {
    if (isClient) {
      const type = detectIdentifierType(identifier);
      if (type === 'email') {
        setHelperText('Email detected');
      } else if (type === 'phone') {
        setHelperText('Phone number detected');
      } else {
        setHelperText('Enter email or phone number');
      }
    }
  }, [identifier, isClient]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const identifierType = detectIdentifierType(identifier);
      
      if (identifierType === 'unknown') {
        setError('Please enter a valid email address or phone number');
        return;
      }

      let data;
      if (identifierType === 'email') {
        data = await login({ email: identifier, password });
      } else {
        data = await loginWithEmailOrPhone({ phone_number: identifier, password });
      }
      loginState(data.access_token);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to login');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%', borderRadius: 2 }}>
          <Typography component="h1" variant="h5" align="center" gutterBottom>
            Sign in
          </Typography>
          
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="identifier"
              label="Email Address or Phone Number"
              name="identifier"
              autoComplete="username"
              autoFocus
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="Enter email or phone number"
              helperText={helperText}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={handleTogglePasswordVisibility}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading}
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </Button>
            <Box sx={{ textAlign: 'center' }}>
              <MuiLink component={Link} href="/register" variant="body2">
                {"Don't have an account? Sign Up"}
              </MuiLink>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}
