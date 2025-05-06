import {Component} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../environmets/environment.prod';

@Component({
  selector: 'app-root',
  styleUrls: ['./app.component.scss'],
  templateUrl: './app.component.html',
  standalone: false
})
export class AppComponent {
  emailText = '';
  result: any = null;

  constructor(private http: HttpClient) {}

  checkSpam() {
    this.http.post(`${environment.apiUrl}/predict`, { text: this.emailText })
      .subscribe(response => this.result = response);
  }
}
