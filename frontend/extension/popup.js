import { API_BASE_URL, DASHBOARD_BASE_URL, USER_ID } from './config.js'

const statusEl = document.getElementById('status')
const pinForm = document.getElementById('pin-form')
const pinInput = document.getElementById('pin-input')
const pinSubmit = document.getElementById('pin-submit')
const pinStatusEl = document.getElementById('pin-status')
const quickPickButtons = document.querySelectorAll('[data-market-id]')
let isPinning = false
const quickPicks = [
  { id: '516710', label: 'US Recession 2025' },
  { id: '516706', label: 'Fed Rate Hike 2025' },
]

function setFooterStatus(message, isError = false) {
  if (!statusEl) return
  statusEl.textContent = message
  statusEl.style.color = isError ? '#f87171' : '#cbd5e1'
}

function setPinStatus(message = '', type) {
  if (!pinStatusEl) return
  pinStatusEl.textContent = message
  pinStatusEl.className = `pin-status${type ? ` ${type}` : ''}`
}

function setPinLoading(loading) {
  if (!pinInput || !pinSubmit) return
  isPinning = loading
  pinInput.disabled = loading
  pinSubmit.disabled = loading
  quickPickButtons.forEach((button) => {
    button.disabled = loading
  })
}

async function pinMarket(marketId) {
  const response = await fetch(`${API_BASE_URL}/api/pin`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ userId: USER_ID, marketId }),
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Failed to pin market')
  }

  return response.json()
}

async function handlePinSubmit(event) {
  event.preventDefault()
  if (isPinning) return
  const rawValue = pinInput.value.trim()
  if (!rawValue) {
    setPinStatus('Please enter a market ID or Polymarket URL', 'error')
    return
  }

  try {
    setPinStatus('Resolving...', 'info')
    setPinLoading(true)
    await pinMarket(rawValue)
    pinInput.value = ''
    setPinStatus("Pinned! We'll watch it for moves.", 'success')
    setFooterStatus('Pinned and syncing ⚡')
  } catch (error) {
    console.error('[Polymarket Scout] pin failed', error)
    const message = error instanceof Error ? error.message : 'Unable to pin market'
    setPinStatus(message, 'error')
    setFooterStatus('Something went wrong. Try again?', true)
  } finally {
    setPinLoading(false)
  }
}

function initPinning() {
  if (!pinForm || !pinInput || !pinSubmit) return
  setPinStatus('')
  pinForm.addEventListener('submit', handlePinSubmit)
  quickPickButtons.forEach((button, index) => {
    const pick = quickPicks[index]
    if (pick) {
      button.textContent = pick.label
      button.dataset.marketId = pick.id
    }
    button.addEventListener('click', () => {
      pinInput.value = button.dataset.marketId ?? ''
      pinInput.focus()
      setPinStatus('')
    })
  })
}

document.addEventListener('DOMContentLoaded', () => {
  initPinning()
  const openDashboardBtn = document.getElementById('open-dashboard')
  if (openDashboardBtn) {
    openDashboardBtn.addEventListener('click', () => {
      chrome.tabs.create({ url: DASHBOARD_BASE_URL })
    })
  }
})
