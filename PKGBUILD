
pkgname=connect-mon-git
_gitname=connect-mon
pkgver=0.0.0
pkgrel=1
pkgdesc="A simple icon to monitor the current internet connection"
arch=('i686' 'x86_64')
url="https://github.com/klieth/connect-mon"
license=('MIT')
depends=('pacman' 'wireless-tools')
conflicts=('connect-mon-git')
provides=('connect-mon-git')
source=('git://github.com/klieth/connect-mon.git')
md5sums=('SKIP')

pkgver() {
	cd $_gitname
	git describe --always | sed 's|-|.|g'
}

package() {
	cd $_gitname
	cp .* "$pkgdir/"
}
