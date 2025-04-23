import {Component} from '@angular/core';
import {HttpClient} from '@angular/common/http';

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
    this.http.post('http://localhost:8000/predict', { text: this.emailText })
      .subscribe(response => this.result = response);
  }
}
