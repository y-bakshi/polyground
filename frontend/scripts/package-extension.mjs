import { mkdir, rm } from 'node:fs/promises'
import path from 'node:path'
import AdmZip from 'adm-zip'

const rootDir = path.resolve(new URL('..', import.meta.url).pathname)
const extensionDir = path.join(rootDir, 'extension')
const distDir = path.join(rootDir, 'extension-dist')
const outputZip = path.join(distDir, 'polymarket-scout-extension.zip')

async function main() {
  await rm(distDir, { recursive: true, force: true })
  await mkdir(distDir, { recursive: true })

  const zip = new AdmZip()
  zip.addLocalFolder(extensionDir)
  zip.writeZip(outputZip)

  console.log(`✓ Packaged extension -> ${outputZip}`)
}

main().catch((error) => {
  console.error('Failed to package extension', error)
  process.exit(1)
})
