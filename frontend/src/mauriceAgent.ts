import { RTVIClient, RTVIClientOptions, RTVIEvent } from '@pipecat-ai/client-js'
import { WebSocketTransport } from '@pipecat-ai/websocket-transport'

export class MauriceVoiceAgent {
  private client: RTVIClient | null = null
  private connectBtn: HTMLButtonElement
  private disconnectBtn: HTMLButtonElement
  private statusIndicator: HTMLElement
  private statusText: HTMLElement
  private voiceIndicator: HTMLElement
  private voiceWave: HTMLElement
  private conversationLog: HTMLElement
  private botAudio: HTMLAudioElement
  private isConnected = false

  constructor() {
    this.setupElements()
    this.setupEventListeners()
    this.setupAudio()
  }

  private setupElements(): void {
    this.connectBtn = document.getElementById('connect-btn') as HTMLButtonElement
    this.disconnectBtn = document.getElementById('disconnect-btn') as HTMLButtonElement
    this.statusIndicator = document.getElementById('status-indicator') as HTMLElement
    this.statusText = document.getElementById('status-text') as HTMLElement
    this.voiceIndicator = document.getElementById('voice-indicator') as HTMLElement
    this.voiceWave = document.getElementById('voice-wave') as HTMLElement
    this.conversationLog = document.getElementById('conversation-log') as HTMLElement

    if (!this.connectBtn || !this.disconnectBtn || !this.statusIndicator || 
        !this.statusText || !this.voiceIndicator || !this.voiceWave || !this.conversationLog) {
      throw new Error('Required DOM elements not found')
    }
  }

  private setupEventListeners(): void {
    this.connectBtn.addEventListener('click', () => this.connect())
    this.disconnectBtn.addEventListener('click', () => this.disconnect())
  }

  private setupAudio(): void {
    this.botAudio = document.createElement('audio')
    this.botAudio.autoplay = true
    this.botAudio.playsInline = true
    document.body.appendChild(this.botAudio)
  }

  private updateStatus(status: 'connected' | 'connecting' | 'disconnected', message: string): void {
    this.statusText.textContent = message
    
    // Remove all status classes
    this.statusIndicator.className = 'w-2 h-2 rounded-full mr-2'
    
    switch (status) {
      case 'connected':
        this.statusIndicator.classList.add('bg-maurice-green')
        break
      case 'connecting':
        this.statusIndicator.classList.add('bg-yellow-400')
        break
      case 'disconnected':
        this.statusIndicator.classList.add('bg-red-500')
        break
    }
  }

  private addToConversation(type: 'user' | 'bot' | 'system', message: string): void {
    // Clear placeholder if it exists
    if (this.conversationLog.children.length === 1 && 
        this.conversationLog.children[0].textContent?.includes('Conversation will appear here')) {
      this.conversationLog.innerHTML = ''
    }

    const messageElement = document.createElement('div')
    messageElement.classList.add('conversation-message')

    switch (type) {
      case 'user':
        messageElement.classList.add('conversation-user')
        messageElement.textContent = `You: ${message}`
        break
      case 'bot':
        messageElement.classList.add('conversation-bot')
        messageElement.textContent = `Maurice: ${message}`
        break
      case 'system':
        messageElement.classList.add('conversation-system')
        messageElement.textContent = message
        break
    }

    this.conversationLog.appendChild(messageElement)
    this.conversationLog.scrollTop = this.conversationLog.scrollHeight
  }

  private setupAudioTrack(track: MediaStreamTrack): void {
    if (this.botAudio.srcObject && 'getAudioTracks' in this.botAudio.srcObject) {
      const existingTrack = this.botAudio.srcObject.getAudioTracks()[0]
      if (existingTrack?.id === track.id) return
    }
    this.botAudio.srcObject = new MediaStream([track])
  }

  private animateVoiceActivity(active: boolean): void {
    if (active) {
      this.voiceWave.classList.add('scale-100', 'animate-pulse-slow')
      this.voiceIndicator.classList.add('border-maurice-blue')
    } else {
      this.voiceWave.classList.remove('scale-100', 'animate-pulse-slow')
      this.voiceIndicator.classList.remove('border-maurice-blue')
    }
  }

  public async connect(): Promise<void> {
    if (this.isConnected) return

    try {
      this.updateStatus('connecting', 'Connecting...')
      this.connectBtn.disabled = true
      this.addToConversation('system', 'Initializing connection...')

      const config: RTVIClientOptions = {
        params: {
          baseUrl: 'http://localhost:7860',
          endpoints: {
            connect: '/connect'
          }
        },
        transport: new WebSocketTransport(),
        callbacks: {
          onConnected: () => {
            this.updateStatus('connected', 'Connected')
            this.isConnected = true
            this.connectBtn.disabled = true
            this.disconnectBtn.disabled = false
            this.addToConversation('system', 'Connected to Maurice!')
          },
          onDisconnected: () => {
            this.updateStatus('disconnected', 'Disconnected')
            this.isConnected = false
            this.connectBtn.disabled = false
            this.disconnectBtn.disabled = true
            this.addToConversation('system', 'Disconnected from Maurice')
            this.animateVoiceActivity(false)
          },
          onBotReady: (data) => {
            this.addToConversation('system', 'Maurice is ready to chat!')
            console.log('Bot ready:', data)
            this.setupMediaTracks()
          },
          onError: (error) => {
            console.error('RTVI Client error:', error)
            this.addToConversation('system', `Connection error: ${error.message || 'Unknown error'}`)
            // Don't disconnect on service errors, just log them
          },
          onUserTranscript: (data) => {
            if (data.final) {
              this.addToConversation('user', data.text)
              this.animateVoiceActivity(false)
            } else {
              this.animateVoiceActivity(true)
            }
          },
          onBotTranscript: (data) => {
            this.addToConversation('bot', data.text)
          },
          onMessageError: (error) => {
            console.error('Message error:', error)
            this.addToConversation('system', `Error: ${error.message || 'Unknown error'}`)
          },
          onError: (error) => {
            console.error('Client error:', error)
            this.addToConversation('system', `Connection error: ${error.message || 'Unknown error'}`)
            this.updateStatus('disconnected', 'Error')
          }
        }
      }

      this.client = new RTVIClient(config)
      this.setupTrackListeners()

      this.addToConversation('system', 'Initializing microphone...')
      await this.client.initDevices()

      this.addToConversation('system', 'Connecting to server...')
      await this.client.connect()

    } catch (error) {
      console.error('Connection error:', error)
      this.addToConversation('system', `Failed to connect: ${error instanceof Error ? error.message : 'Unknown error'}`)
      this.updateStatus('disconnected', 'Connection failed')
      this.connectBtn.disabled = false
      this.isConnected = false
    }
  }

  public async disconnect(): Promise<void> {
    if (!this.client || !this.isConnected) return

    try {
      this.addToConversation('system', 'Disconnecting...')
      await this.client.disconnect()
      
      // Clean up audio
      if (this.botAudio.srcObject && 'getAudioTracks' in this.botAudio.srcObject) {
        this.botAudio.srcObject.getAudioTracks().forEach(track => track.stop())
        this.botAudio.srcObject = null
      }
      
      this.client = null
    } catch (error) {
      console.error('Disconnect error:', error)
      this.addToConversation('system', `Disconnect error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  private setupMediaTracks(): void {
    if (!this.client) return
    
    const tracks = this.client.tracks()
    if (tracks.bot?.audio) {
      this.setupAudioTrack(tracks.bot.audio)
    }
  }

  private setupTrackListeners(): void {
    if (!this.client) return

    this.client.on(RTVIEvent.TrackStarted, (track, participant) => {
      if (!participant?.local && track.kind === 'audio') {
        this.setupAudioTrack(track)
      }
    })

    this.client.on(RTVIEvent.TrackStopped, (track, participant) => {
      console.log(`Track stopped: ${track.kind} from ${participant?.name || 'unknown'}`)
    })
  }
}