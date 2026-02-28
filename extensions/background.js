/**
 * Prompt Makeover Chrome Extension - Background Service Worker
 * Handles context menu creation and actions
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

/**
 * Create context menu items on extension install
 */
chrome.runtime.onInstalled.addListener(() => {
  // Enable side panel to open on extension icon click
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });

  // Main context menu item
  chrome.contextMenus.create({
    id: 'promptMakeoverRoot',
    title: '✨ Prompt Makeover',
    contexts: ['selection']
  });

  // Optimize selected text
  chrome.contextMenus.create({
    id: 'optimizeSelection',
    parentId: 'promptMakeoverRoot',
    title: 'Optimize this selection',
    contexts: ['selection']
  });

  // Separator
  chrome.contextMenus.create({
    id: 'separator1',
    parentId: 'promptMakeoverRoot',
    type: 'separator',
    contexts: ['selection']
  });

  // Open side panel
  chrome.contextMenus.create({
    id: 'openSidePanel',
    parentId: 'promptMakeoverRoot',
    title: '📋 Open Side Panel',
    contexts: ['selection', 'page']
  });

  console.log('Prompt Makeover context menus created');
});

/**
 * Handle context menu clicks
 */
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'optimizeSelection') {
    await handleOptimizeSelection(info, tab);
  } else if (info.menuItemId === 'openSidePanel') {
    await handleOpenSidePanel(tab);
  }
});

/**
 * Optimize the selected text
 */
async function handleOptimizeSelection(info, tab) {
  const selectedText = info.selectionText.trim();

  if (!selectedText) {
    return;
  }

  // Open side panel
  await chrome.sidePanel.open({ windowId: tab.windowId });

  // Wait a bit for the side panel to open
  await new Promise(resolve => setTimeout(resolve, 500));

  // Send message to side panel with the selected text
  try {
    const [sidePanelTab] = await chrome.tabs.query({ url: chrome.runtime.getURL('sidepanel.html') });

    if (sidePanelTab) {
      chrome.tabs.sendMessage(sidePanelTab.id, {
        action: 'autoOptimize',
        prompt: selectedText
      });
    }
  } catch (error) {
    console.error('Failed to send message to side panel:', error);
  }
}

/**
 * Open the side panel
 */
async function handleOpenSidePanel(tab) {
  try {
    await chrome.sidePanel.open({ windowId: tab.windowId });
  } catch (error) {
    console.error('Failed to open side panel:', error);
  }
}
