import { Component } from '@angular/core';
import { concat } from 'rxjs';
import { StatusService } from "../../services/status.service";

@Component({
  selector: 'home',
  templateUrl: './home.component.html'
})
export class HomeComponent {
    status: object;
    constructor(private httpMessageService: StatusService) { 
      this.httpMessageService.getStatus().toPromise().then(msg => {
        this.status = msg;
      });
    }
    
}
