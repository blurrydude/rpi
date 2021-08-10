import { Component, Input, Output } from '@angular/core';
import {Md5} from 'ts-md5/dist/md5';
import {NgbModal, ModalDismissReasons} from '@ng-bootstrap/ng-bootstrap';
import { NgForm } from '@angular/forms';
import { StatusService } from './services/status.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  @Input() @Output() user: string = "";
  @Input() @Output() pass: string = "";

  constructor(private modalService: NgbModal, public httpMessageService: StatusService) {}

  title = 'command-center';

  public login(f: NgForm) {
    this.httpMessageService.getToken(f.value.user, Md5.hashStr(f.value.pass)).toPromise().then(msg => {
      for (const [k, v] of Object.entries(msg)) {
        if(k == "auth") {
          this.httpMessageService.auth = v;
        }
      }
      if(this.httpMessageService.auth == "invalid") {
        // do something
        console.log("no no, bad dog");
        this.httpMessageService.auth = "";
        return;
      }
      this.httpMessageService.user = f.value.user;
      this.modalService.dismissAll();
    });
  }

  public launch_login(content: any) {
    console.log("launch login");
    this.modalService.open(content, {ariaLabelledBy: 'modal-basic-title'});
  }
}
