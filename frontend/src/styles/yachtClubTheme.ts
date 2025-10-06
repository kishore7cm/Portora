// Yacht Club Theme Configuration
export const yachtClubTheme = {
  name: 'Yacht Club Premium',
  colors: {
    primary: '#1C3D5A',        // Primary Navy
    secondary: '#7A5C45',      // Secondary Brown
    accent: '#C9A66B',         // Accent Sand Gold
    background: '#FDFBF7',     // Background Light
    cardBeige: '#EDE9E3',      // Card Beige
    text: '#000000',           // Black for headings
    textSecondary: '#5A6A73',  // Neutral Blue-Gray for body
    danger: '#DC2626',         // Danger Red
    warning: '#C9A66B',        // Gold for warnings
    success: '#22C55E'         // Success Green
  },
  styles: {
    // Card styles
    card: 'bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border',
    cardHover: 'hover:shadow-2xl hover:-translate-y-1',
    
    // Text styles
    heading: 'font-bold text-navy-900',
    subheading: 'font-semibold text-navy-800',
    bodyText: 'text-blue-gray-600',
    
    // Button styles
    primaryButton: 'bg-navy-800 hover:bg-gold-500 text-white transition-colors duration-200 px-4 py-2 rounded-lg font-medium',
    secondaryButton: 'bg-beige-100 hover:bg-gold-100 text-navy-800 transition-colors duration-200 px-4 py-2 rounded-lg font-medium',
    
    // Alert styles
    successAlert: 'bg-green-50 border border-green-200 text-green-800 rounded-lg p-4',
    warningAlert: 'bg-gold-50 border border-gold-200 text-brown-700 rounded-lg p-4',
    dangerAlert: 'bg-red-50 border border-red-200 text-red-800 rounded-lg p-4',
    
    // Input styles
    input: 'border border-beige-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-gold-400 focus:border-gold-400',
    
    // Navigation styles
    tabActive: 'bg-navy-800 text-white border-gold-400',
    tabInactive: 'bg-beige-100 text-navy-700 hover:bg-gold-100'
  },
  
  // Helper functions for inline styles
  getCardStyle: () => ({
    backgroundColor: '#FFFFFF',
    borderColor: '#EDE9E3',
    boxShadow: '0 4px 6px -1px rgba(237, 233, 227, 0.25), 0 2px 4px -1px rgba(237, 233, 227, 0.15)'
  }),
  
  getCardHoverStyle: () => ({
    boxShadow: '0 10px 25px -5px rgba(201, 166, 107, 0.2), 0 4px 6px -2px rgba(237, 233, 227, 0.25)'
  }),
  
  getHeaderStyle: () => ({
    color: '#000000',
    borderBottom: '2px solid #C9A66B'
  }),
  
  getSubHeaderStyle: () => ({
    color: '#1C3D5A',
    borderBottom: '2px solid #C9A66B'
  }),
  
  getMetricCardStyle: () => ({
    backgroundColor: 'rgba(237, 233, 227, 0.2)',
    border: '1px solid rgba(237, 233, 227, 0.6)'
  }),
  
  getSuccessStyle: () => ({
    backgroundColor: 'rgba(34, 197, 94, 0.1)',
    borderColor: '#22C55E',
    color: '#1C3D5A'
  }),
  
  getWarningStyle: () => ({
    backgroundColor: 'rgba(201, 166, 107, 0.1)',
    borderColor: '#C9A66B',
    color: '#7A5C45'
  }),
  
  getDangerStyle: () => ({
    backgroundColor: 'rgba(220, 38, 38, 0.1)',
    borderColor: '#DC2626',
    color: '#1C3D5A'
  })
}

export default yachtClubTheme
