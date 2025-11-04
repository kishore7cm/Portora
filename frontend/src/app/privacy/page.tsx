import Navbar from '@/components/site/Navbar'
import Footer from '@/components/site/Footer'
import Container from '@/components/ui/Container'

export default function PrivacyPage() {
  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-soft">
        <Container className="py-12 md:py-20">
          <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-12 text-center">
              <h1 className="text-4xl md:text-5xl font-bold text-neutral-900 mb-4">
                Privacy Policy
              </h1>
              <p className="text-lg text-neutral-600">
                Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
              </p>
            </div>

            {/* Content */}
            <div className="bg-white rounded-2xl shadow-medium border border-neutral-200 p-8 md:p-12 space-y-8">
              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">1. Introduction</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  Welcome to Portora ("we," "our," or "us"). We are committed to protecting your privacy and ensuring the security of your personal information. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our portfolio management platform and services.
                </p>
                <p className="text-neutral-600 leading-relaxed">
                  By using Portora, you agree to the collection and use of information in accordance with this policy. If you do not agree with our policies and practices, please do not use our services.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">2. Information We Collect</h2>
                <h3 className="text-xl font-semibold text-neutral-900 mb-3">2.1 Personal Information</h3>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  We collect information that you provide directly to us, including:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Name, email address, and contact information</li>
                  <li>Account credentials and authentication information</li>
                  <li>Profile information and preferences</li>
                  <li>Financial and portfolio data that you choose to import or enter</li>
                  <li>Communication preferences and support inquiries</li>
                </ul>

                <h3 className="text-xl font-semibold text-neutral-900 mb-3">2.2 Automatically Collected Information</h3>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  When you use Portora, we automatically collect certain information, including:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Device information (IP address, browser type, operating system)</li>
                  <li>Usage data and interaction patterns</li>
                  <li>Log files and technical diagnostics</li>
                  <li>Cookies and similar tracking technologies</li>
                </ul>

                <h3 className="text-xl font-semibold text-neutral-900 mb-3">2.3 Financial Data</h3>
                <p className="text-neutral-600 leading-relaxed">
                  When you connect your accounts or import portfolio data, we may collect and store:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2">
                  <li>Investment holdings and transaction history</li>
                  <li>Account balances and valuations</li>
                  <li>Market data and performance metrics</li>
                  <li>Asset allocation and sector information</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">3. How We Use Your Information</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  We use the information we collect to:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Provide, maintain, and improve our services</li>
                  <li>Process your transactions and manage your account</li>
                  <li>Generate portfolio insights, analytics, and recommendations</li>
                  <li>Send you updates, alerts, and communications about your portfolio</li>
                  <li>Respond to your inquiries and provide customer support</li>
                  <li>Detect, prevent, and address technical issues and security threats</li>
                  <li>Comply with legal obligations and enforce our terms</li>
                  <li>Analyze usage patterns to enhance user experience</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">4. Data Security</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  We implement industry-standard security measures to protect your personal and financial information:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>End-to-end encryption for data in transit and at rest</li>
                  <li>Secure authentication and access controls</li>
                  <li>Regular security audits and vulnerability assessments</li>
                  <li>Compliance with industry security standards (SOC 2, ISO 27001)</li>
                  <li>Restricted access to personal data on a need-to-know basis</li>
                </ul>
                <p className="text-neutral-600 leading-relaxed">
                  However, no method of transmission over the internet or electronic storage is 100% secure. While we strive to use commercially acceptable means to protect your information, we cannot guarantee absolute security.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">5. Data Sharing and Disclosure</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  We do not sell, rent, or trade your personal information. We may share your information only in the following circumstances:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li><strong>Service Providers:</strong> With trusted third-party vendors who assist in operating our platform (data hosting, analytics, payment processing) under strict confidentiality agreements</li>
                  <li><strong>Legal Requirements:</strong> When required by law, court order, or government regulation</li>
                  <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets (with notice to users)</li>
                  <li><strong>With Your Consent:</strong> When you explicitly authorize us to share your information</li>
                  <li><strong>Aggregated Data:</strong> We may share anonymized, aggregated data that cannot identify you</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">6. Your Rights and Choices</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  You have the following rights regarding your personal information:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li><strong>Access:</strong> Request a copy of the personal data we hold about you</li>
                  <li><strong>Correction:</strong> Update or correct inaccurate information</li>
                  <li><strong>Deletion:</strong> Request deletion of your personal data (subject to legal retention requirements)</li>
                  <li><strong>Portability:</strong> Export your data in a machine-readable format</li>
                  <li><strong>Opt-Out:</strong> Unsubscribe from marketing communications at any time</li>
                  <li><strong>Account Closure:</strong> Close your account and request data deletion</li>
                </ul>
                <p className="text-neutral-600 leading-relaxed">
                  To exercise these rights, please contact us at privacy@portora.ai or through your account settings.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">7. Cookies and Tracking Technologies</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  We use cookies and similar technologies to:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Remember your preferences and settings</li>
                  <li>Analyze how you use our platform</li>
                  <li>Provide personalized content and features</li>
                  <li>Improve security and prevent fraud</li>
                </ul>
                <p className="text-neutral-600 leading-relaxed">
                  You can control cookies through your browser settings. Note that disabling cookies may limit certain features of our service.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">8. Data Retention</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  We retain your personal information for as long as necessary to:
                </p>
                <ul className="list-disc list-inside text-neutral-600 space-y-2 mb-4">
                  <li>Provide our services and maintain your account</li>
                  <li>Comply with legal, tax, and regulatory obligations</li>
                  <li>Resolve disputes and enforce our agreements</li>
                </ul>
                <p className="text-neutral-600 leading-relaxed">
                  When you close your account, we will delete or anonymize your data within 30 days, except where we are required to retain it by law.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">9. Children's Privacy</h2>
                <p className="text-neutral-600 leading-relaxed">
                  Portora is not intended for users under the age of 18. We do not knowingly collect personal information from children. If you believe we have inadvertently collected information from a minor, please contact us immediately.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">10. International Data Transfers</h2>
                <p className="text-neutral-600 leading-relaxed">
                  Your information may be transferred to and processed in countries other than your own. We ensure that appropriate safeguards are in place to protect your data in accordance with applicable data protection laws, including the General Data Protection Regulation (GDPR) and other regional requirements.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">11. Changes to This Privacy Policy</h2>
                <p className="text-neutral-600 leading-relaxed">
                  We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the new policy on this page and updating the "Last updated" date. Your continued use of Portora after such changes constitutes acceptance of the updated policy.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">12. Contact Us</h2>
                <p className="text-neutral-600 leading-relaxed mb-4">
                  If you have questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us:
                </p>
                <div className="bg-neutral-50 rounded-xl p-6 border border-neutral-200">
                  <p className="text-neutral-700 font-semibold mb-2">Portora Privacy Team</p>
                  <p className="text-neutral-600">Email: privacy@portora.ai</p>
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

