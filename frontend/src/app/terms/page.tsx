import Navbar from '@/components/site/Navbar'
import Footer from '@/components/site/Footer'
import Container from '@/components/ui/Container'

export default function TermsPage() {
  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-soft">
        <Container className="py-12 md:py-20">
          <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-12 text-center">
              <h1 className="text-4xl md:text-5xl font-bold text-neutral-900 mb-4">
                Terms of Service
              </h1>
              <p className="text-lg text-neutral-600">
                Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
              </p>
            </div>

            {/* Content */}
            <div className="bg-white rounded-2xl shadow-medium border border-neutral-200 p-8 md:p-12 space-y-8">
              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">1. Agreement to Terms</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  By accessing or using Portora ("the Service"), you agree to be bound by these Terms of Service ("Terms"). If you disagree with any part of these terms, you may not access the Service.
                </p>
                <p className="text-neutral-600 leading-relaxed">
                  These Terms apply to all visitors, users, and others who access or use the Service. You represent that you are at least 18 years old and have the legal capacity to enter into these Terms.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">2. Description of Service</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  Portora is a portfolio management platform that provides:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Portfolio tracking and analytics</li>
                  <li>Investment insights and recommendations</li>
                  <li>Performance monitoring and reporting</li>
                  <li>Data visualization and analysis tools</li>
                  <li>Account aggregation (when available)</li>
                </ul>
                <p className="text-neutral-600 leading-relaxed">
                  We reserve the right to modify, suspend, or discontinue any part of the Service at any time with or without notice.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">3. Account Registration</h2>
                <h3 className="text-xl font-semibold text-neutral-900 mb-3">3.1 Account Creation</h3>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  To use Portora, you must:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Create an account with accurate and complete information</li>
                  <li>Maintain and update your account information</li>
                  <li>Maintain the security of your account credentials</li>
                  <li>Notify us immediately of any unauthorized access</li>
                  <li>Accept responsibility for all activities under your account</li>
                </ul>

                <h3 className="text-xl font-semibold text-neutral-900 mb-3">3.2 Account Security</h3>
                <p className="text-neutral-600 leading-relaxed">
                  You are responsible for maintaining the confidentiality of your account password and for all activities that occur under your account. We are not liable for any loss or damage arising from your failure to protect your account information.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">4. Use of Service</h2>
                <h3 className="text-xl font-semibold text-neutral-900 mb-3">4.1 Permitted Use</h3>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  You may use Portora solely for lawful purposes and in accordance with these Terms. You agree to:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Provide accurate and truthful information</li>
                  <li>Use the Service for personal portfolio management purposes</li>
                  <li>Comply with all applicable laws and regulations</li>
                  <li>Respect intellectual property rights</li>
                </ul>

                <h3 className="text-xl font-semibold text-neutral-900 mb-3">4.2 Prohibited Activities</h3>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  You agree not to:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Use the Service for any illegal or unauthorized purpose</li>
                  <li>Attempt to gain unauthorized access to the Service or its systems</li>
                  <li>Interfere with or disrupt the Service or servers</li>
                  <li>Transmit viruses, malware, or harmful code</li>
                  <li>Reverse engineer, decompile, or disassemble any part of the Service</li>
                  <li>Use automated systems to access the Service without permission</li>
                  <li>Share your account credentials with third parties</li>
                  <li>Impersonate any person or entity</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">5. Financial Information and Data</h2>
                <h3 className="text-xl font-semibold text-neutral-900 mb-3">5.1 Your Data</h3>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  You retain ownership of all data you upload, import, or enter into Portora. By using the Service, you grant us a license to:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Store, process, and display your data as necessary to provide the Service</li>
                  <li>Use anonymized, aggregated data for analytics and improvement</li>
                  <li>Create backups and ensure data availability</li>
                </ul>

                <h3 className="text-xl font-semibold text-neutral-900 mb-3">5.2 Data Accuracy</h3>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  You are solely responsible for the accuracy and completeness of the financial data you provide. Portora:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Does not verify the accuracy of imported or entered data</li>
                  <li>Is not liable for errors, omissions, or inaccuracies in your data</li>
                  <li>Provides tools and features "as is" without warranties</li>
                </ul>

                <h3 className="text-xl font-semibold text-neutral-900 mb-3">5.3 Market Data</h3>
                <p className="text-neutral-600 leading-relaxed">
                  We provide market data, quotes, and financial information from third-party sources. We do not guarantee the accuracy, completeness, or timeliness of such data. Market data is for informational purposes only and should not be considered investment advice.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">6. Investment Advice Disclaimer</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  <strong>Important:</strong> Portora is a portfolio management tool and does not provide investment, financial, legal, or tax advice. All content, insights, and recommendations are for informational purposes only.
                </p>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  You acknowledge and agree that:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>No content on Portora constitutes professional investment advice</li>
                  <li>You should consult qualified financial advisors before making investment decisions</li>
                  <li>Past performance does not guarantee future results</li>
                  <li>All investments carry risk of loss</li>
                  <li>You are solely responsible for your investment decisions</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">7. Subscription and Billing</h2>
                <h3 className="text-xl font-semibold text-neutral-900 mb-3">7.1 Free and Paid Plans</h3>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  Portora may offer both free and paid subscription plans. Features, limitations, and pricing are subject to change with notice.
                </p>

                <h3 className="text-xl font-semibold text-neutral-900 mb-3">7.2 Billing</h3>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  For paid plans:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Subscriptions are billed in advance on a recurring basis</li>
                  <li>All fees are non-refundable except as required by law</li>
                  <li>You authorize us to charge your payment method automatically</li>
                  <li>Price changes will be communicated with advance notice</li>
                </ul>

                <h3 className="text-xl font-semibold text-neutral-900 mb-3">7.3 Cancellation</h3>
                <p className="text-neutral-600 leading-relaxed">
                  You may cancel your subscription at any time. Cancellation takes effect at the end of the current billing period. No refunds are provided for partial billing periods.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">8. Intellectual Property</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  The Service, including its original content, features, functionality, logos, and design, is owned by Portora and protected by international copyright, trademark, and other intellectual property laws.
                </p>
                <p className="text-neutral-600 leading-relaxed">
                  You may not reproduce, distribute, modify, create derivative works of, publicly display, or otherwise use the Service or its content without our prior written permission.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">9. Limitation of Liability</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  TO THE MAXIMUM EXTENT PERMITTED BY LAW:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Portora is provided "as is" and "as available" without warranties of any kind</li>
                  <li>We disclaim all warranties, express or implied, including merchantability and fitness for a particular purpose</li>
                  <li>We are not liable for any indirect, incidental, special, or consequential damages</li>
                  <li>Our total liability shall not exceed the amount you paid us in the 12 months preceding the claim</li>
                  <li>We are not responsible for losses arising from your investment decisions</li>
                  <li>We do not guarantee uninterrupted, error-free, or secure access to the Service</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">10. Indemnification</h2>
                <p className="text-neutral-600 leading-relaxed">
                  You agree to indemnify, defend, and hold harmless Portora, its officers, directors, employees, and agents from any claims, damages, losses, liabilities, and expenses (including legal fees) arising from:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mt-4">
                  <li>Your use of the Service</li>
                  <li>Your violation of these Terms</li>
                  <li>Your violation of any rights of another party</li>
                  <li>Any inaccurate or incomplete data you provide</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">11. Termination</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  We may suspend or terminate your access to the Service immediately, without prior notice, if:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>You breach these Terms</li>
                  <li>You engage in fraudulent, abusive, or illegal activity</li>
                  <li>We are required to do so by law</li>
                  <li>You request account deletion</li>
                </ul>
                <p className="text-neutral-600 leading-relaxed">
                  Upon termination, your right to use the Service will cease immediately. You may request deletion of your data, subject to our data retention policies.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">12. Third-Party Services</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  Portora may integrate with or link to third-party services, including:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Financial data providers and aggregators</li>
                  <li>Payment processors</li>
                  <li>Cloud hosting and infrastructure services</li>
                </ul>
                <p className="text-neutral-600 leading-relaxed">
                  Your use of third-party services is subject to their respective terms and privacy policies. We are not responsible for the practices or content of third-party services.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">13. Dispute Resolution</h2>
                <h3 className="text-xl font-semibold text-neutral-900 mb-3">13.1 Governing Law</h3>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  These Terms shall be governed by and construed in accordance with the laws of [Your Jurisdiction], without regard to conflict of law principles.
                </p>

                <h3 className="text-xl font-semibold text-neutral-900 mb-3">13.2 Dispute Resolution Process</h3>
                <p className="text-neutral-600 leading-relaxed">
                  Any disputes arising from these Terms or your use of the Service shall be resolved through good faith negotiation. If negotiation fails, disputes shall be resolved through binding arbitration in accordance with the rules of [Arbitration Organization], except where prohibited by law.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">14. Changes to Terms</h2>
                <p className="text-neutral-600 leading-relaxed">
                  We reserve the right to modify these Terms at any time. We will notify you of material changes by:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mt-4 mb-4">
                  <li>Posting the updated Terms on this page</li>
                  <li>Sending an email notification to your registered address</li>
                  <li>Displaying a notice within the Service</li>
                </ul>
                <p className="text-neutral-600 leading-relaxed">
                  Your continued use of Portora after changes become effective constitutes acceptance of the updated Terms. If you do not agree, you must stop using the Service.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">15. Severability</h2>
                <p className="text-neutral-600 leading-relaxed">
                  If any provision of these Terms is found to be unenforceable or invalid, that provision shall be limited or eliminated to the minimum extent necessary, and the remaining provisions shall remain in full force and effect.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">16. Entire Agreement</h2>
                <p className="text-neutral-600 leading-relaxed">
                  These Terms, together with our Privacy Policy, constitute the entire agreement between you and Portora regarding the Service and supersede all prior agreements and understandings.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">17. Contact Information</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  If you have questions about these Terms, please contact us:
                </p>
                <div className="bg-neutral-50 rounded-xl p-6 border border-neutral-200">
                  <p className="text-neutral-700 font-semibold mb-2">Portora Legal Team</p>
                  <p className="text-neutral-600">Email: legal@portora.ai</p>
                  <p className="text-neutral-600">Address: [Your Company Address]</p>
                </div>
              </section>
            </div>
          </div>
        </Container>
      </div>
      <Footer />
    </>
  )
}

