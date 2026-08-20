import { environment } from '../../../../environment';
import { url } from 'inspector';
import { Observable, Subject } from 'rxjs';
import { Inject, Injectable, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class ChatserviceService {
  private socket?: WebSocket;
  chatUrl: string = environment.chatServiceUrl

  private messageSubject = new Subject<any>();

  messages$ = this.messageSubject.asObservable();

  constructor(
    @Inject(PLATFORM_ID) private platformId: Object
  ) { }

  connect(): void {

    // IMPORTANT: WebSocket should only run in browser
    if (!isPlatformBrowser(this.platformId)) {
      console.log('SSR: WebSocket not created');
      return;
    }

    console.log('Browser: Creating WebSocket');

    this.socket = new WebSocket(this.chatUrl);

    this.socket.onopen = () => {
      console.log('WebSocket connected');
    };

    this.socket.onmessage = (event) => {

      console.log('Message received:', event.data);

      const data = JSON.parse(event.data);

      this.messageSubject.next(data);
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
    };
  }

  sendMessage(message: any): void {

    if (
      this.socket &&
      this.socket.readyState === WebSocket.OPEN
    ) {
      this.socket.send(JSON.stringify(message));
    }
  }

  disconnect(): void {

    this.socket?.close();
    this.socket = undefined;
  }
}
