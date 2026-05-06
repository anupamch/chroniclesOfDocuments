'use client';

import { Box, Typography, Link } from '@mui/material';

export default function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        borderTop: '1px solid',
        borderColor: 'divider',
        backgroundColor: 'background.paper',
      }}
    >
      <Typography variant="body2" color="text.secondary" align="center">
        {'Chronicles of Documents © '}
        {new Date().getFullYear()}
        {' | '}
        <Link color="inherit" href="https://github.com" target="_blank">
          Documentation
        </Link>
        {' | '}
        <Link color="inherit" href="/api/health" target="_blank">
          API Status
        </Link>
      </Typography>
      <Typography variant="caption" color="text.secondary" align="center" display="block" sx={{ mt: 1 }}>
        Multi-agentic document analysis powered by AI
      </Typography>
    </Box>
  );
}
