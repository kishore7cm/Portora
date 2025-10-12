'use client'

import React from 'react'
import ThemedInsightsTab from '../../components/ThemedInsightsTab'
import YachtLayout from '@/components/Layout/YachtLayout'

const ThemedInsightsPage: React.FC = () => {
  return (
    <YachtLayout 
      title="Themed Insights" 
      subtitle="Yacht Club Premium – Advanced Portfolio Analytics"
    >
      <ThemedInsightsTab />
    </YachtLayout>
  )
}

export default ThemedInsightsPage
