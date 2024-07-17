function cellDFC = CreateDFC(dfcCenterAER,dfcRadialSize,nVertexs)

% Refs
% [x,y,z] = sph2cart(azimuth,elevation,r)
% [A,E,R] = [azimuth,elevation,r] = cart2sph(X,Y,Z)


% Structures
% center = [x,y,z]
%% Passing parameters
    % Mean radius of DFC in radians
    cellDFC.radialSize      = dfcRadialSize;    
    % Center of current DFC in Spherical coordinates
    cellDFC.center.AER      = dfcCenterAER;
    % Cartesian version of center
    [dummyX,dummyY,dummyZ]  = sph2cart(...
                                cellDFC.center.AER(1),...
                                cellDFC.center.AER(2),...
                                cellDFC.center.AER(3));
    cellDFC.center.XYZ      = [dummyX,dummyY,dummyZ];

    
%% Adding Contour    
    cellDFC.contour.XYZ = zeros(nVertexs,3);
    cellDFC.contour.AER = zeros(nVertexs,3);
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