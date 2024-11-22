import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import BoltIcon from '@mui/icons-material/Bolt';

function Header() {
  return (
    <AppBar position="static" sx={{ mb: 4 }}>
      <Toolbar>
        <Box display="flex" alignItems="center">
          <BoltIcon sx={{ mr: 2, fontSize: 32 }} />
          <Typography variant="h1" sx={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
            ThunderData
          </Typography>
        </Box>
        <Typography variant="subtitle1" sx={{ ml: 2, color: 'rgba(255, 255, 255, 0.7)' }}>
          Advanced Text Processing
        </Typography>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
