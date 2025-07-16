import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const FarmManagement: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Farm Management
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Farm Management Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            This page will contain farm management features including:
          </Typography>
          <ul>
            <li>Farm registration and profile management</li>
            <li>Geospatial farm boundary mapping</li>
            <li>Crop type and rotation tracking</li>
            <li>Historical yield data</li>
            <li>Insurance policy management</li>
          </ul>
        </CardContent>
      </Card>
    </Box>
  );
};

export default FarmManagement; 