import { CommandCenterPage } from './app.po';

describe('command-center App', function() {
  let page: CommandCenterPage;

  beforeEach(() => {
    page = new CommandCenterPage();
  });

  it('should display message saying app works', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('app works!');
  });
});
