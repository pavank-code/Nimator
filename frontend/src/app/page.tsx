import Navbar from '../components/landing/Navbar';
import HeroSection from '../components/landing/HeroSection';
import Stats from '../components/landing/Stats';
import HowItWorks from '../components/landing/HowItWorks';
import ProductShowcase from '../components/landing/ProductShowcase';
import WhoItsFor from '../components/landing/WhoItsFor';
import WhatMakesDifferent from '../components/landing/WhatMakesDifferent';
import PhilosophySection from '../components/landing/PhilosophySection';
import WhyThisExists from '../components/landing/WhyThisExists';
import BehindTheScenes from '../components/landing/BehindTheScenes';
import FAQ from '../components/landing/FAQ';
import FinalCTA from '../components/landing/FinalCTA';
import Footer from '../components/landing/Footer';

export default function LandingPage() {
  return (
    <main className="min-h-screen">
      <Navbar />
      <HeroSection />
      <Stats />
      <HowItWorks />
      <ProductShowcase />
      <WhoItsFor />
      <WhatMakesDifferent />
      <PhilosophySection />
      <WhyThisExists />
      <BehindTheScenes />
      <FAQ />
      <FinalCTA />
      <Footer />
    </main>
  );
}