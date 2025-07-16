import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  Agriculture as FarmIcon,
  Assessment as RiskIcon,
  Warning as AlertIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

// Mock data - in real app, this would come from API
const mockData = {
  totalFarms: 156,
  totalArea: 12450,
  averageRisk: 0.42,
  riskDistribution: [
    { name: 'Low Risk', value: 45, color: '#4caf50' },
    { name: 'Medium Risk', value: 78, color: '#ff9800' },
    { name: 'High Risk', value: 33, color: '#f44336' },
  ],
  recentAssessments: [
    { farm: 'Green Valley Farm', risk: 0.35, date: '2024-01-15' },
    { farm: 'Sunset Ranch', risk: 0.68, date: '2024-01-14' },
    { farm: 'Prairie Fields', risk: 0.22, date: '2024-01-13' },
    { farm: 'Mountain View', risk: 0.51, date: '2024-01-12' },
  ],
  alerts: [
    { type: 'high_risk', message: '3 farms require immediate attention', count: 3 },
    { type: 'weather', message: 'Severe weather warning for Midwest region', count: 1 },
    { type: 'assessment', message: '15 farms due for reassessment', count: 15 },
  ],
  monthlyTrends: [
    { month: 'Jan', assessments: 45, claims: 2 },
    { month: 'Feb', assessments: 52, claims: 1 },
    { month: 'Mar', assessments: 48, claims: 3 },
    { month: 'Apr', assessments: 61, claims: 0 },
    { month: 'May', assessments: 58, claims: 1 },
    { month: 'Jun', assessments: 67, claims: 2 },
  ],
};

const Dashboard: React.FC = () => {
  const [data, setData] = useState(mockData);

  useEffect(() => {
    // In real app, fetch data from API
    // fetchDashboardData().then(setData);
  }, []);

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    subtitle?: string;
    icon: React.ReactNode;
    color?: string;
  }> = ({ title, value, subtitle, icon, color = 'primary.main' }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              backgroundColor: color,
              color: 'white',
              borderRadius: 2,
              p: 1,
              mr: 2,
            }}
          >
            {icon}
          </Box>
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 600 }}>
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {title}
            </Typography>
          </Box>
        </Box>
        {subtitle && (
          <Typography variant="caption" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  const RiskCard: React.FC<{ farm: string; risk: number; date: string }> = ({
    farm,
    risk,
    date,
  }) => {
    const getRiskColor = (risk: number) => {
      if (risk < 0.3) return '#4caf50';
      if (risk < 0.7) return '#ff9800';
      return '#f44336';
    };

    const getRiskLabel = (risk: number) => {
      if (risk < 0.3) return 'Low';
      if (risk < 0.7) return 'Medium';
      return 'High';
    };

    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                {farm}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {date}
              </Typography>
            </Box>
            <Chip
              label={getRiskLabel(risk)}
              sx={{
                backgroundColor: getRiskColor(risk),
                color: 'white',
                fontWeight: 600,
              }}
            />
          </Box>
          <Box sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Risk Score: {(risk * 100).toFixed(0)}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={risk * 100}
              sx={{
                mt: 0.5,
                height: 6,
                borderRadius: 3,
                backgroundColor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getRiskColor(risk),
                },
              }}
            />
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Dashboard Overview
      </Typography>

      {/* Alerts */}
      {data.alerts.length > 0 && (
        <Box sx={{ mb: 3 }}>
          {data.alerts.map((alert, index) => (
            <Alert
              key={index}
              severity={alert.type === 'high_risk' ? 'error' : alert.type === 'weather' ? 'warning' : 'info'}
              sx={{ mb: 1 }}
            >
              {alert.message}
            </Alert>
          ))}
        </Box>
      )}

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Farms"
            value={data.totalFarms}
            subtitle={`${data.totalArea.toLocaleString()} hectares`}
            icon={<FarmIcon />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Average Risk"
            value={`${(data.averageRisk * 100).toFixed(0)}%`}
            subtitle="Portfolio-wide"
            icon={<RiskIcon />}
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Alerts"
            value={data.alerts.length}
            subtitle="Require attention"
            icon={<AlertIcon />}
            color="#f44336"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Monthly Growth"
            value="+12%"
            subtitle="vs last month"
            icon={<TrendingIcon />}
            color="#2196f3"
          />
        </Grid>
      </Grid>

      {/* Charts and Details */}
      <Grid container spacing={3}>
        {/* Risk Distribution Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Risk Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={data.riskDistribution}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {data.riskDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Monthly Trends */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Monthly Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data.monthlyTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="assessments" fill="#2e7d32" name="Assessments" />
                  <Bar dataKey="claims" fill="#f44336" name="Claims" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Assessments */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Recent Assessments
              </Typography>
              {data.recentAssessments.map((assessment, index) => (
                <RiskCard
                  key={index}
                  farm={assessment.farm}
                  risk={assessment.risk}
                  date={assessment.date}
                />
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Chip
                  label="Run New Assessment"
                  color="primary"
                  variant="outlined"
                  sx={{ justifyContent: 'flex-start', py: 1 }}
                />
                <Chip
                  label="View High Risk Farms"
                  color="error"
                  variant="outlined"
                  sx={{ justifyContent: 'flex-start', py: 1 }}
                />
                <Chip
                  label="Generate Portfolio Report"
                  color="secondary"
                  variant="outlined"
                  sx={{ justifyContent: 'flex-start', py: 1 }}
                />
                <Chip
                  label="Update Weather Alerts"
                  color="info"
                  variant="outlined"
                  sx={{ justifyContent: 'flex-start', py: 1 }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 