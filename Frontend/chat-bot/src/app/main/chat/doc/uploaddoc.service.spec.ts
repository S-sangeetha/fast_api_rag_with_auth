import { TestBed } from '@angular/core/testing';

import { UploaddocService } from './uploaddoc.service';

describe('UploaddocService', () => {
  let service: UploaddocService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UploaddocService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
