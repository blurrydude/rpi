import { Component } from '@angular/core';
import { concat } from 'rxjs';
import { StatusService } from "../../services/status.service";

@Component({
  selector: 'home',
  templateUrl: './home.component.html'
})
export class HomeComponent {
    status: Array<string>;
    constructor(private httpMessageService: StatusService) { 
      this.httpMessageService.getStatus().toPromise().then(msg => {
        for(var k in msg) {
          this.status.push(k + ": " + msg[k] + " W")
        }
      });
    }
    
}
