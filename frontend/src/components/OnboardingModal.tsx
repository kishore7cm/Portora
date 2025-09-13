'use client';

import { useState, useEffect } from 'react';
import { X, ChevronRight, ChevronLeft, CheckCircle, BarChart3, TrendingUp, Bot, Users, Target, Zap } from 'lucide-react';

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

const onboardingSteps = [
  {
    id: 1,
    title: "Welcome to EaseLi",
    subtitle: "Your Personal Portfolio Management Platform",
    content: "EaseLi helps you track, analyze, and optimize your investment portfolio with advanced analytics and automated trading bots.",
    icon: <Zap className="w-12 h-12 text-blue-600" />,
    features: [
      "Real-time portfolio tracking",
      "Advanced analytics & projections",
      "S&P 500 market analysis",
      "Automated trading bots"
    ]
  },
  {
    id: 2,
    title: "Portfolio Overview",
    subtitle: "Track Your Investments",
    content: "Monitor your portfolio performance with real-time data, allocation charts, and detailed analytics.",
    icon: <BarChart3 className="w-12 h-12 text-green-600" />,
    features: [
      "Net worth tracking",
      "Gain/loss analysis",
      "Asset allocation visualization",
      "Performance projections"
    ]
  },
  {
    id: 3,
    title: "Market Analysis",
    subtitle: "S&P 500 Intelligence",
    content: "Get comprehensive analysis of S&P 500 stocks with technical indicators and intelligent scoring.",
    icon: <TrendingUp className="w-12 h-12 text-purple-600" />,
    features: [
      "Technical analysis (RSI, MACD)",
      "Intelligent scoring system",
      "Sector performance tracking",
      "Top gainers & losers"
    ]
  },
  {
    id: 4,
    title: "Trading Bots",
    subtitle: "Automate Your Strategy",
    content: "Deploy automated trading bots with various strategies to optimize your portfolio performance.",
    icon: <Bot className="w-12 h-12 text-orange-600" />,
    features: [
      "DCA (Dollar Cost Averaging)",
      "Momentum trading",
      "Mean reversion strategies",
      "Grid trading systems"
    ]
  },
  {
    id: 5,
    title: "Community & Benchmarks",
    subtitle: "Compare & Learn",
    content: "Benchmark your performance against market indices and community averages to stay competitive.",
    icon: <Users className="w-12 h-12 text-indigo-600" />,
    features: [
      "Performance benchmarking",
      "Community comparisons",
      "Model portfolio analysis",
      "Risk-adjusted returns"
    ]
  },
  {
    id: 6,
    title: "Portfolio Health",
    subtitle: "Optimize Your Strategy",
    content: "Get personalized insights on your portfolio health with diversification, concentration, and risk analysis.",
    icon: <Target className="w-12 h-12 text-red-600" />,
    features: [
      "Health score (0-100)",
      "Diversification analysis",
      "Concentration risk",
      "Asset drift tracking"
    ]
  }
];

export default function OnboardingModal({ isOpen, onClose, onComplete }: OnboardingModalProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isCompleting, setIsCompleting] = useState(false);

  const handleNext = () => {
    if (currentStep < onboardingSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    setIsCompleting(true);
    try {
      // Call API to mark onboarding as complete
      const response = await fetch('http://localhost:8000/onboarding/complete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        // Store in localStorage for demo
        localStorage.setItem('hasSeenOnboarding', 'true');
        onComplete();
      }
    } catch (error) {
      console.error('Error completing onboarding:', error);
      // Still complete locally for demo
      localStorage.setItem('hasSeenOnboarding', 'true');
      onComplete();
    } finally {
      setIsCompleting(false);
    }
  };

  const handleSkip = () => {
    localStorage.setItem('hasSeenOnboarding', 'true');
    onClose();
  };

  if (!isOpen) return null;

  const currentStepData = onboardingSteps[currentStep];
  const isLastStep = currentStep === onboardingSteps.length - 1;
  const isFirstStep = currentStep === 0;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
              {currentStep + 1}
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Getting Started</h2>
              <p className="text-sm text-gray-500">Step {currentStep + 1} of {onboardingSteps.length}</p>
            </div>
          </div>
          <button
            onClick={handleSkip}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-2">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / onboardingSteps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Content */}
        <div className="p-6 flex-1 overflow-y-auto">
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              {currentStepData.icon}
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              {currentStepData.title}
            </h3>
            <p className="text-lg text-gray-600 mb-4">
              {currentStepData.subtitle}
            </p>
            <p className="text-gray-700 leading-relaxed">
              {currentStepData.content}
            </p>
          </div>

          {/* Features List */}
          <div className="space-y-3">
            {currentStepData.features.map((feature, index) => (
              <div key={index} className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                <span className="text-gray-700">{feature}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t bg-gray-50">
          <button
            onClick={handlePrevious}
            disabled={isFirstStep}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              isFirstStep
                ? 'text-gray-400 cursor-not-allowed'
                : 'text-gray-700 hover:bg-gray-200'
            }`}
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>

          <div className="flex space-x-2">
            <button
              onClick={handleSkip}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Skip Tour
            </button>
            <button
              onClick={handleNext}
              disabled={isCompleting}
              className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isCompleting ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : isLastStep ? (
                <>
                  <span>Get Started</span>
                  <CheckCircle className="w-4 h-4" />
                </>
              ) : (
                <>
                  <span>Next</span>
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
