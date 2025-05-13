export default function Header() {
  return (
    <header className="p-6 bg-green-600 text-white">
      <nav className="flex justify-between items-center">
        <div className="text-3xl font-bold">Wallie</div>
        <ul className="flex space-x-6">
          <li><a href="#about" className="hover:text-green-300">Sobre</a></li>
          <li><a href="#creators" className="hover:text-green-300">Criadores</a></li>
          <li><a href="#whatsapp" className="hover:text-green-300">Bot WhatsApp</a></li>
        </ul>
      </nav>
    </header>
  )
}