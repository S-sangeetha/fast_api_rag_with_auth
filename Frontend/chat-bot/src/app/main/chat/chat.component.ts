import { Component, OnInit, OnDestroy, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { ChatserviceService } from './chatservice.service';
import { UploaddocService } from './doc/uploaddoc.service';

export interface ChatMessage {
  type: 'user' | 'bot';
  text: string;
}

@Component({
  selector: 'app-chat',
  standalone: false,
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.css'
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('scrollContainer') private scrollContainer!: ElementRef;

  messages: ChatMessage[] = [];
  isLoading: boolean = false;
  selectedFile: any
  constructor(private websocketService: ChatserviceService, private uploadService: UploaddocService) { }

  ngOnInit(): void {
    this.websocketService.connect();

    this.websocketService.messages$.subscribe(message => {
      console.log('Bot response received:', message);

      // Stop loading spinner
      this.isLoading = false;

      let botText = '';
      if (typeof message === 'string') {
        botText = message;
      } else if (message && typeof message === 'object') {
        botText = message.response || message.answer || message.text || message.message || message.data || JSON.stringify(message);
      } else {
        botText = String(message);
      }

      this.messages.push({
        type: 'bot',
        text: botText
      });
    });
  }

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    try {
      if (this.scrollContainer) {
        this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
      }
    } catch (err) { }
  }

  sendMessage(question: string): void {
    if (!question || !question.trim() || this.isLoading) {
      return;
    }

    // Add user message to UI
    this.messages.push({
      type: 'user',
      text: question.trim()
    });

    // Set loading state until WebSocket response arrives
    this.isLoading = true;

    // Send question to WebSocket backend
    this.websocketService.sendMessage(question.trim());
  }

  ngOnDestroy(): void {
    this.websocketService.disconnect();
  }
  uploadFile(event: Event): void {
    const input = event.target as HTMLInputElement;

    if (!input.files || input.files.length === 0) {
      return;
    }

    const file = input.files[0];
    const formData = new FormData();
    formData.append('file', file);

    // Show upload prompt in user chat
    this.messages.push({
      type: 'user',
      text: `Uploading file: ${file.name}`
    });

    this.isLoading = true;

    this.uploadService.upload_doc(formData).subscribe({
      next: (response: any) => {
        console.log('Upload successful:', response);
        this.isLoading = false;
        const successMsg = response?.message || 'Uploaded successfully!';
        this.messages.push({
          type: 'bot',
          text: `📄 "${file.name}" - ${successMsg}`
        });
        input.value = '';
      },
      error: (error) => {
        console.error('Upload failed:', error);
        this.isLoading = false;
        const errorDetail = error?.error?.detail || 'Failed to upload document. Please try again.';
        this.messages.push({
          type: 'bot',
          text: `⚠️ Upload failed: ${errorDetail}`
        });
        input.value = '';
      }
    });
  }
}
