import { Component, Input, Output } from '@angular/core';
import { StatusService } from "../../services/status.service";
import { GoogleChartComponent } from 'angular-google-charts';  

@Component({
  selector: 'home',
  templateUrl: './home.component.html'
})
export class HomeComponent {
    @Output() status: object = {};
    @Output() pistatus: object = {};
    @Output() readings: object = {};
    @Output() checkins: object = {};
    @Output() motionsensors: object = {};
    @Output() thsensors: object = {};
    @Output() doors: object = {};
    @Output() rollers: object = {};
    @Output() totalPower: number = 0.0;
    @Output() sysmonlog: any = [];
    @Output() apilog: any = [];
    @Output() mode: any = [];
    @Output() fast: boolean = false;
    @Output() live: boolean = true;
    @Output() local: boolean = true;
    firstLoad: boolean = true;

    @Output() @Input() chartData: any = {
      title: 'Temperatures',
      type: 'LineChart',
      data: [
      ],
      columnNames: [''],
      options: {
        hAxis: {
           title: ''
        },
        vAxis:{
           title: 'Temperature',
           viewWindow: {
            max:95,
            min:65
          }
        },
        //colors: ['#e0440e', '#e6693e']
      },
      width: 1200,
      height: 400
    }
    constructor(public httpMessageService: StatusService) { 
      this.load(httpMessageService, true)
    }

    public sendThermosettings(room: string, temp_low: number, temp_high: number, humidity: number, circ_min: number, hum_circ_min: number, stage_limit: number, stage_cooldown: number) {
      this.httpMessageService.sendThermosettings(room,temp_low,temp_high,humidity,circ_min,hum_circ_min, stage_limit, stage_cooldown).toPromise().then(smsg => {
        setTimeout(()=>{this.load(this.httpMessageService,false)},500);
      });
    }

    public command(com: string) {
      this.httpMessageService.sendCommand(com).toPromise().then(smsg => {
        setTimeout(()=>{this.load(this.httpMessageService,false)},3000);
      });
    }

    public getLogs() {
      this.httpMessageService.getSysMonLog().toPromise().then(lmsg => {
        this.sysmonlog = lmsg;
      });
    }

    public getApiLogs() {
      this.httpMessageService.getApiLog().toPromise().then(lmsg => {
        this.apilog = lmsg;
      });
    }

    public load(httpMessageService: StatusService, main_loop: boolean) {
      if(main_loop == true) setTimeout(()=>{this.load(httpMessageService, true)},this.fast?5000:15000);
      if(this.live == false && this.firstLoad == false) return;
      if(this.firstLoad == true) this.firstLoad = false;
      this.httpMessageService.getMode().toPromise().then(mmsg => {
        this.mode = mmsg;
      });
      this.httpMessageService.getMotionSensors().toPromise().then(hmsg => {
        this.motionsensors = hmsg;
      });
      this.httpMessageService.getReadings().toPromise().then(rmsg => {
        this.readings = rmsg;
        this.httpMessageService.getPassiveReadings().toPromise().then(prmsg => {
          this.thsensors = prmsg;
          
          let row = [this.chartData.data.length];
          let cooling_main = 0;
          let cooling_gameroom = 0;
          for (const [k, v] of Object.entries(this.readings)) {
            if(this.chartData.columnNames.indexOf(k)===-1) {
              this.chartData.columnNames.push(k);
            }
            if(k == "gameroom") {
              cooling_gameroom = v['cooling'] == 'on' ? 93:0;
            }
            if(k == "hallway") {
              cooling_main = v['cooling'] === 'on' ? 94:0;
            }
            row.push(parseFloat(v["temperature"]));
          }
          for (const [k, v] of Object.entries(this.thsensors)) {
            if(this.chartData.columnNames.indexOf(v["label"])===-1) {
              this.chartData.columnNames.push(v["label"]);
            }
            row.push(parseFloat(v["temperature"]));
          }
          row.push(cooling_main);
          row.push(cooling_gameroom);
          if(this.chartData.columnNames.indexOf("Main A/C")===-1) {
            this.chartData.columnNames.push("Main A/C");
          }
          if(this.chartData.columnNames.indexOf("Secondary A/C")===-1) {
            this.chartData.columnNames.push("Secondary A/C");
          }
          this.chartData.data.push(row);
          this.chartData.data = Object.assign([], this.chartData.data);
        });
      });
      this.httpMessageService.getDoors().toPromise().then(dmsg => {
        this.doors = dmsg;
      });
      this.httpMessageService.getRollers().toPromise().then(bmsg => {
        this.rollers = bmsg;
      });

      this.httpMessageService.getStatus().toPromise().then(msg => {
        this.status = msg;
        this.totalPower = 0.0;
        for (const [k, v] of Object.entries(this.status)) {
          this.totalPower += parseFloat(v["power"])
        }
        this.httpMessageService.getPiStatus().toPromise().then(smsg => {
          this.pistatus = smsg;
          for (const [k, v] of Object.entries(this.pistatus)) {
            let s = v["heartbeat"].split('_');
            let d = s[0].split('/');
            let t = s[1];
            let ms = Date.parse(d[2]+"-"+d[0]+"-"+d[1]+"T"+t+".000-04:00");
            let dt = new Date(ms);
            let n = new Date();
            let c = n.getTime() - ms;
            v["class"] = c > 150000 ? "text-danger" : c < 0 ? "text-info" : "text-success";
            v["heartbeat"] = dt;
          }
          this.httpMessageService.getCheckins().toPromise().then(cmsg => {
            this.checkins = cmsg;
            for (const [k, v] of Object.entries(this.checkins)) {
              for (const [sk, sv] of Object.entries(this.status)) {
                if(k != sk) continue;
                if(v.indexOf("NONCOMM") > -1) {
                  sv["checkin"] = "fas fa-tired"
                  continue;
                }
                let s = v.split(', ');
                let d = s[0].split('/');
                let t = s[1];
                let ms = Date.parse(d[2]+"-"+d[0]+"-"+d[1]+"T"+t+".000-04:00");
                let dt = new Date(ms);
                let n = new Date();
                let c = n.getTime() - ms;
                sv["checkin"] = c > 150000 ? "fas fa-dizzy" : c < 0 ? "far fa-question-circle" : "fas fa-signal";
                sv["heartbeat"] = dt;
              }
            }
          });
        });
      });
    }
    
}
