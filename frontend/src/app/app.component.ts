import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from './shared/components/sidebar/sidebar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, SidebarComponent],
  template: `
    <div class="flex h-screen overflow-hidden">
      <app-sidebar />
      <main class="flex-1 overflow-y-auto bg-gray-50">
        <router-outlet />
      </main>
    </div>
  `,
})
export class AppComponent {}
