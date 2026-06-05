import { Routes } from '@angular/router';
import { Home } from './pages/home/home';
import { Relatorios } from './pages/relatorios/relatorios';

export const routes: Routes = [
  {
    path: '',
    component: Home
  },
  {
    path: 'relatorios',
    component: Relatorios
  }
];