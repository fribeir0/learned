export default function Hero() {
  return (
    <section className="flex items-center justify-center h-screen bg-gradient-to-r from-green-400 via-blue-500 to-purple-600 text-center">
      <div className="text-white">
        <h1 className="text-5xl font-bold mb-4">
          Transformando o Mundo com Inteligência Artificial Sustentável
        </h1>
        <p className="text-xl mb-8">
          Wallie está ajudando a criar um futuro mais verde, com ações sustentáveis usando IA. Conheça o Wallie e comece a transformar seu mundo!
        </p>
        <a href="https://wa.me/1234567890" className="px-8 py-3 bg-green-600 rounded-lg text-white hover:bg-green-700">
          Fale com o Wallie no WhatsApp
        </a>
      </div>
    </section>
  )
}