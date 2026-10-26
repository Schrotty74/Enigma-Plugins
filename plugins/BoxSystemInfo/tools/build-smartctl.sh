#!/bin/sh
# Requires Zig 0.14.1, make, tar and a POSIX shell. No global installations.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
: "${ZIG:?Set ZIG to the absolute path of Zig 0.14.1}"
case "$ZIG" in /*) ;; *) echo 'ZIG must be an absolute path' >&2; exit 1 ;; esac
[ "$("$ZIG" version)" = '0.14.1' ] || { echo 'Zig 0.14.1 required' >&2; exit 1; }
WORK=$(mktemp -d "$ROOT/.smartctl-rebuild.XXXXXX")
trap 'rm -rf "$WORK"' EXIT HUP INT TERM
export ZIG
export ZIG_GLOBAL_CACHE_DIR="$WORK/cache"
DOC="$ROOT/src/usr/share/doc/boxsysteminfo/smartmontools"
tar -xzf "$DOC/smartmontools-7.4.tar.gz" -C "$WORK"
mkdir "$WORK/obj"
cat > "$WORK/cc" <<'CC'
#!/bin/sh
exec "$ZIG" cc -target arm-linux-musleabihf -mcpu=generic+v7a+vfp3d16 "$@"
CC
cat > "$WORK/cxx" <<'CXX'
#!/bin/sh
exec "$ZIG" c++ -target arm-linux-musleabihf -mcpu=generic+v7a+vfp3d16 "$@"
CXX
chmod +x "$WORK/cc" "$WORK/cxx"
export CC="$WORK/cc" CXX="$WORK/cxx"
export SOURCE_DATE_EPOCH=1690887634
export CFLAGS='-Os -g0' CXXFLAGS='-Os -g0' LDFLAGS='-static -s'
BUILD=$("$WORK/smartmontools-7.4/config.guess")
(cd "$WORK/obj" && ../smartmontools-7.4/configure --build="$BUILD" --host=arm-linux-musleabihf --without-libcap-ng --without-selinux --without-libsystemd --with-update-smart-drivedb=no && make -j2 smartctl)
cp "$WORK/obj/smartctl" "$ROOT/src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo/bin/smartctl"
chmod 755 "$ROOT/src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo/bin/smartctl"
echo 'Built static ARMv7 smartctl; rebuild IPK with ./build.sh'
