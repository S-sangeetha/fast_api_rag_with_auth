import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MainRoutingModule } from './main-routing.module';
import { MainComponent } from './main/main.component';
import { ChatComponent } from './chat/chat.component';


@NgModule({
  declarations: [
    MainComponent,
    ChatComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    MainRoutingModule
  ]
})
export class MainModule { }
