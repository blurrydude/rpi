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
      //type: 'ComboChart',
      type: 'LineChart',
      data: [
      ],
      columnNames: ['',
        'GR Temp',
        'GR Hum',
        'GR Cool',
        'GR Heat',
        'GR Fan',
        'WHF',
        'HW Temp',
        'HW Hum',
        'HW Cool',
        'HW Heat',
        'HW Fan',
        'WHF',
        'DR Temp',
        'DR Hum',
        'Deck Temp',
        'Deck Hum'
      ],
      options: {
        backgroundColor: "#212529",
        titleTextStyle: {
          color: "#fff"
        },
        legend: {
          textStyle: {
            color: "#fff"
          },
          titleTextStyle: {
            color: "#fff"
          }
        },
        hAxis: {
           title: '',
           textStyle: {
             color: "#fff"
           },
           titleTextStyle: {
             color: "#fff"
           }
        },
        vAxis:{
           title: 'Temperature',
          //  viewWindow: {
          //   max:110,
          //   min:-10
          // },
          textStyle: {
            color: "#fff"
          },
          titleTextStyle: {
            color: "#fff"
          },
           gridlines: {
             color: "#777"
           }
        },
      //  seriesType: 'bars',
      //  series: {
      //    0: {type: 'line'},
      //    1: {type: 'line'},
      //     //2: {type: 'line'},
      //     //3: {type: 'line'},
      //     //4: {type: 'line'},
      //     //5: {type: 'line'},
      //    6: {type: 'line'},
      //    7: {type: 'line'},
      //     //8: {type: 'line'},
      //     //9: {type: 'line'},
      //     //10: {type: 'line'},
      //     //11: {type: 'line'},
      //    12: {type: 'line'},
      //    13: {type: 'line'},
      //    14: {type: 'line'},
      //    15: {type: 'line'},
      //    16: {type: 'line'}
      //  }
       series: {
        0: {lineWidth: 3},
        1: {lineWidth: 3},
        2: {lineWidth: 1},
        3: {lineWidth: 1},
        4: {lineWidth: 1},
        5: {lineWidth: 1},
        6: {lineWidth: 5},
        7: {lineWidth: 5},
        8: {lineWidth: 2},
        9: {lineWidth: 2},
        10: {lineWidth: 2},
        11: {lineWidth: 2},
        12: {lineWidth: 3},
        13: {lineWidth: 3},
        14: {lineWidth: 3},
        15: {lineWidth: 3}
      },
        colors: [
          '#ff9999',
          '#9999ff',
          '#ff99ff',
          '#99ffff',
          '#99ff99',
          '#337733',

          '#ff0000',
          '#0000ff',
          '#ff00ff',
          '#00ffff',
          '#00ff00',
          '#007700',
          
          '#ffaaaa',
          '#aaaaff',
          '#ffcccc',
          '#ccccff'
        ],
      lineWidth: 3
      },
      width: 1295,
      height: 800
    }

    @Output() @Input() chartData2: any = {
      title: 'Power',
      //type: 'ComboChart',
      type: 'LineChart',
      data: [
      ],
      columnNames: [''],
      options: {
        backgroundColor: "#212529",
        titleTextStyle: {
          color: "#fff"
        },
        legend: {
          textStyle: {
            color: "#fff"
          },
          titleTextStyle: {
            color: "#fff"
          }
        },
        hAxis: {
           title: '',
           textStyle: {
             color: "#fff"
           },
           titleTextStyle: {
             color: "#fff"
           }
        },
        vAxis:{
           title: 'Power (W)',
           textStyle: {
             color: "#fff"
           },
           titleTextStyle: {
             color: "#fff"
           },
            gridlines: {
              color: "#777"
            }
          //  viewWindow: {
          //   max:85,
          //   min:55
          // }
        },
        lineWidth: 2
      },
      width: 1295,
      height: 800
    }

    @Output() @Input() chartData3: any = {
      title: 'Power',
      //type: 'ComboChart',
      type: 'Gauge',
      data: [
        ["Power (kW)",0]
      ],
      options: {
        backgroundColor: "#212529",
        width: 200,
        height: 200,
        greenFrom: 0,
        greenTo: 25,
        redFrom: 60,
        redTo: 100,
        yellowFrom: 25,
        yellowTo: 60,
        minorTicks: 5,
        majorTicks: ['0W','250W','500W','750W','1kW']  // <-- add major ticks
      }
      // width: 1295,
      // height: 800
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
      this.httpMessageService.getTemplog().toPromise().then(hmsg => {
        this.chartData.data = hmsg;
        for (const v of this.chartData.data) {
          v[3] = v[3] == 1 ? 4 : v[3];
          v[4] = v[4] == 1 ? 6 : v[4];
          v[5] = v[5] == 1 ? 8 : v[5];
          v[6] = v[6] == 1 ? 10 : v[6];

          v[9] = v[9] == 1 ? 12 : v[9];
          v[10] = v[10] == 1 ? 14 : v[10];
          v[11] = v[11] == 1 ? 16 : v[11];
          v[12] = v[12] == 1 ? 18 : v[12];
        }
        this.chartData.data = Object.assign([], this.chartData.data);
      });
      this.httpMessageService.getPowerlog().toPromise().then(hmsg => {
        this.chartData2.data = hmsg;
        // for (const v of this.chartData2.data) {
        //   v.pop(v.length-1);
        // }
        this.chartData2.data = Object.assign([], this.chartData2.data);
        let last = this.chartData2.data[this.chartData2.data.length-1];
        this.chartData3.data = [["Power",
          //last[last.length-1]
          {
            v:Math.round((last[last.length-1]/1000)*100),
            f:last[last.length-1]+" W"
          }
        ]];
        this.chartData3.data = Object.assign([], this.chartData3.data);
      });
      this.httpMessageService.getReadings().toPromise().then(rmsg => {
        this.readings = rmsg;
        this.httpMessageService.getPassiveReadings().toPromise().then(prmsg => {
          this.thsensors = prmsg;
          /*
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
          */
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
          if(this.chartData2.columnNames.indexOf(k)===-1) {
            this.chartData2.columnNames.push(k);
          }
          this.totalPower += parseFloat(v["power"])
        }
        if(this.chartData2.columnNames.indexOf("Total")===-1) {
          this.chartData2.columnNames.push("Total");
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
