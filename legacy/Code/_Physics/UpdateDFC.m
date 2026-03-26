function cellDFC = UpdateDFC(enviroment,indexDFC)
% Basic copy
    cellDFC = enviroment.layerDFC.cellDFC(indexDFC);
%% Passing parameters
%cellDFC.radialSize    
%cellDFC.center.AER
% Cartesian version of center
%    [dummyX,dummyY,dummyZ]  = sph2cart(...
%                                cellDFC.center.AER(1),...
%                                cellDFC.center.AER(2),...
%                                cellDFC.center.AER(3));
%    cellDFC.center.XYZ      = [dummyX,dummyY,dummyZ];
    dfcRadialSize      = cellDFC.radialSize;
    marginVelocity     = enviroment.embryoData.layerEVL.marginVelocity;
    
    noisyVelocity      = 2*(rand -0.5) * marginVelocity.AER(2) /2;
    dfcVelocity.AER    = marginVelocity.AER + ...
                        [noisyVelocity,...
                         noisyVelocity,...
                         0];
    
%% Update DFC center
    % Center of current DFC in Spherical coordinates
    cellDFC.center.AER = cellDFC.center.AER + dfcVelocity.AER;
    % Cartesian version of center
    [dummyX,dummyY,dummyZ]  = sph2cart(...
                                cellDFC.center.AER(1),...
                                cellDFC.center.AER(2),...
                                cellDFC.center.AER(3));
    cellDFC.center.XYZ      = [dummyX,dummyY,dummyZ];

%% Updating Contour    
    nVertexs = size(cellDFC.contour.XYZ,1);
    % Filling contour position
    % Updating Spherical coordinates    
    % [azimuth,elevation,r] = cart2sph(X,Y,Z)  
    
    stepAngle    = (2*pi) /nVertexs;
    currentAngle = 0;
    for indexContour = 1:nVertexs
        cellDFC.contour.AER(indexContour,1) = ...
            cellDFC.center.AER(1) + dfcRadialSize * cos(currentAngle);
        cellDFC.contour.AER(indexContour,2) = ...
            cellDFC.center.AER(2) + dfcRadialSize * sin(currentAngle);
        cellDFC.contour.AER(indexContour,3) = cellDFC.center.AER(3);
        currentAngle = currentAngle + stepAngle;
    end
    
    % Updating Cartesian coordinates
    % [x,y,z] = sph2cart(azimuth,elevation,r)
    [dummyX,dummyY,dummyZ] = sph2cart(...
                                cellDFC.contour.AER(:,1),...
                                cellDFC.contour.AER(:,2),...
                                cellDFC.contour.AER(:,3));
    cellDFC.contour.XYZ    = [dummyX,dummyY,dummyZ];
end

