import { API_BASE_URL, DASHBOARD_BASE_URL, USER_ID } from './config.js'

const pinnedListEl = document.getElementById('pinned-list')
const pinnedEmptyEl = document.getElementById('pinned-empty')
const alertsListEl = document.getElementById('alerts-list')
const alertsEmptyEl = document.getElementById('alerts-empty')
const alertsCountEl = document.getElementById('alerts-count')
const statusEl = document.getElementById('status')

async function fetchJSON(path) {
  const response = await fetch(`${API_BASE_URL}${path}`)
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`)
  }
  return response.json()
}

function renderPinned(markets = []) {
  pinnedListEl.innerHTML = ''
  if (!markets.length) {
    pinnedEmptyEl.hidden = false
    return
  }
  pinnedEmptyEl.hidden = true
  markets.forEach((market) => {
    const li = document.createElement('li')
    li.className = 'pinned-item'
    const info = document.createElement('div')
    const title = document.createElement('h3')
    title.textContent = market.title
    const meta = document.createElement('p')
    meta.textContent = `${market.impliedProbability.toFixed(1)}% • Δ ${market.changePct.toFixed(1)}%`
    info.appendChild(title)
    info.appendChild(meta)

    const button = document.createElement('button')
    button.type = 'button'
    button.textContent = 'Open'
    button.addEventListener('click', () => openMarket(market.marketId))

    li.appendChild(info)
    li.appendChild(button)
    pinnedListEl.appendChild(li)
  })
}

function renderAlerts(alerts = []) {
  alertsListEl.innerHTML = ''
  alertsCountEl.textContent = alerts.filter((alert) => !alert.seen).length
  if (!alerts.length) {
    alertsEmptyEl.hidden = false
    return
  }
  alertsEmptyEl.hidden = true

  alerts.slice(0, 4).forEach((alert) => {
    const li = document.createElement('li')
    li.className = 'alert'
    const title = document.createElement('strong')
    title.textContent = alert.marketTitle
    const meta = document.createElement('span')
    meta.textContent = `${alert.changePct.toFixed(1)}% in window`
    const body = document.createElement('p')
    body.textContent = alert.insightText
    li.appendChild(title)
    li.appendChild(meta)
    li.appendChild(body)
    li.addEventListener('click', () => openMarket(alert.marketId))
    alertsListEl.appendChild(li)
  })
}

function openMarket(marketId) {
  chrome.tabs.create({ url: `${DASHBOARD_BASE_URL}/market/${marketId}` })
}

function updateStatus(message, isError = false) {
  statusEl.textContent = message
  statusEl.style.color = isError ? '#f87171' : '#94a3b8'
}

async function loadData() {
  updateStatus('Refreshing…')
  try {
    const [pinnedPayload, alertsPayload] = await Promise.all([
      fetchJSON(`/api/pinned?userId=${USER_ID}`),
      fetchJSON(`/api/alerts?userId=${USER_ID}`),
    ])
    renderPinned(pinnedPayload.items ?? [])
    renderAlerts(alertsPayload.alerts ?? [])
    updateStatus('Synced just now')
  } catch (error) {
    console.error('[Polymarket Scout] popup refresh failed', error)
    updateStatus('Failed to refresh. Is the API running?', true)
  }
}

document.getElementById('refresh').addEventListener('click', loadData)
document.getElementById('open-dashboard').addEventListener('click', () => {
  chrome.tabs.create({ url: DASHBOARD_BASE_URL })
})

document.addEventListener('DOMContentLoaded', () => {
  loadData()
})
