import Head from 'next/head'
import Header from '../components/Header'
import Hero from '../components/Hero'
import About from '../components/About'
import Creators from '../components/Creators'
import WhatsAppCTA from '../components/WhatsAppCTA'
import Footer from '../components/Footer'

export default function Home() {
  return (
    <div className="bg-gray-900 text-white">
      <Head>
        <title>Wallie - Transformando o Mundo com IA</title>
        <meta name="description" content="Wallie, o robô que promove um futuro mais sustentável" />
      </Head>
      
      <Header />
      <Hero />
      <About />
      <Creators />
      <WhatsAppCTA />
      <Footer />
    </div>
  )
}