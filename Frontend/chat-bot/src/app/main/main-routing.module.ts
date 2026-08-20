import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MainComponent } from './main/main.component';
import { ChatComponent } from './chat/chat.component';

const routes: Routes = [{
  path: '',
  component: MainComponent,
  children: [
    {
      path: 'chat',
      component: ChatComponent
    }
  ]
}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class MainRoutingModule { }
