// Yacht Club Premium Chart Theme Configuration
export const yachtChartTheme = {
  // Color palette for charts
  colors: [
    "#1C3D5A", // Primary Navy
    "#7A5C45", // Secondary Brown  
    "#C9A66B", // Accent Sand Gold
    "#5A6A73", // Text Secondary
    "#EDE9E3", // Card Beige
    "#FDFBF7", // Background Light
    "#22C55E", // Success Green
    "#DC2626"  // Danger Red
  ],
  
  // Chart area styling
  chartArea: {
    backgroundColor: 'transparent',
    border: 'none'
  },
  
  // Tooltip styling
  tooltip: {
    backgroundColor: '#FDFBF7',
    border: '1px solid #C9A66B',
    borderRadius: '8px',
    color: '#1C3D5A',
    fontSize: '14px',
    fontWeight: '500'
  },
  
  // Axis styling
  axis: {
    stroke: '#5A6A73',
    strokeWidth: 1,
    fontSize: '12px',
    color: '#5A6A73'
  },
  
  // Grid styling
  grid: {
    stroke: '#EDE9E3',
    strokeWidth: 1,
    strokeDasharray: '3 3'
  },
  
  // Legend styling
  legend: {
    color: '#1C3D5A',
    fontSize: '12px',
    fontWeight: '500'
  },
  
  // Responsive container styling
  responsiveContainer: {
    width: '100%',
    height: '100%'
  }
}

// Helper function to get chart colors
export const getChartColors = (count: number) => {
  return yachtChartTheme.colors.slice(0, count)
}

// Helper function to get gradient colors
export const getGradientColors = (baseColor: string) => {
  return {
    start: baseColor,
    end: `${baseColor}20`
  }
}

export default yachtChartTheme
