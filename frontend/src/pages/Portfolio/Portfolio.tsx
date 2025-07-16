import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Portfolio: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Portfolio Management
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Insurance Portfolio Overview
          </Typography>
          <Typography variant="body1" color="text.secondary">
            This page will contain portfolio management features including:
          </Typography>
          <ul>
            <li>Portfolio-wide risk exposure analysis</li>
            <li>Geographic risk distribution mapping</li>
            <li>Premium revenue tracking and forecasting</li>
            <li>Claims history and loss ratio analysis</li>
            <li>Portfolio optimization recommendations</li>
            <li>Regulatory compliance reporting</li>
          </ul>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Portfolio; 