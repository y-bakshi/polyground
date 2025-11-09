import { API_BASE_URL, DASHBOARD_BASE_URL, USER_ID, ALERTS_POLL_MINUTES } from './config.js'

const ALERTS_ENDPOINT = `${API_BASE_URL}/api/alerts?userId=${USER_ID}`

async function fetchAlerts() {
  const response = await fetch(ALERTS_ENDPOINT)
  if (!response.ok) {
    throw new Error(`Failed to fetch alerts: ${response.status}`)
  }
  const payload = await response.json()
  return payload.alerts ?? []
}

async function updateBadge() {
  try {
    const alerts = await fetchAlerts()
    const unread = alerts.filter((alert) => !alert.seen).length
    await chrome.action.setBadgeBackgroundColor({ color: '#f97316' })
    await chrome.action.setBadgeText({ text: unread > 0 ? String(unread) : '' })
    await maybeNotify(alerts)
  } catch (error) {
    console.error('[Polymarket Scout] badge update failed', error)
    await chrome.action.setBadgeText({ text: '!' })
  }
}

async function maybeNotify(alerts) {
  if (!alerts?.length) return
  const latest = alerts[0]
  const stored = await chrome.storage.local.get(['lastAlertId'])
  if (stored.lastAlertId === latest.id) return

  await chrome.storage.local.set({ lastAlertId: latest.id })
  const message = `${latest.marketTitle}\nΔ ${latest.changePct}% • Threshold ${latest.threshold}%`

  await chrome.notifications.create(`alert-${latest.id}`, {
    type: 'basic',
    iconUrl: 'icons/icon-128.png',
    priority: 0,
    title: 'New Polymarket alert',
    message,
  })
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create('alerts-poll', { periodInMinutes: ALERTS_POLL_MINUTES })
  chrome.action.setBadgeText({ text: '' })
  updateBadge()
})

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'alerts-poll') {
    updateBadge()
  }
})

chrome.notifications.onClicked.addListener((notificationId) => {
  if (!notificationId.startsWith('alert-')) return
  const marketId = notificationId.replace('alert-', '')
  chrome.tabs.create({ url: `${DASHBOARD_BASE_URL}/market/${marketId}` })
})
